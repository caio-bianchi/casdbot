import pandas as pd
import urllib.parse
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import ssl
import smtplib

from selenium import webdriver # Abrir navegador
from selenium.webdriver.common.keys import Keys # Enviar as mensagens
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib
import socket
import utils


# ADDITIONAL_TOOLS_FIELD = '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/div/div/div/span'

def is_media(file_extension: str) -> bool:
    media_types = set(['png', 'svg', 'jpeg', 'jpg', 'gif', 'mp4', '3gpp'])
    return file_extension in media_types

class Bot:
    def __init__(self, sender_email: str | None = None, email_password: str | None = None):
        self.sender_email = sender_email
        self.email_password = email_password
        self.file_queue = []

    def clear_queue(self):
        self.file_queue = []

    def add_to_queue(self, file_path: str):
        self.file_queue.append(file_path)

    def is_connected(self) -> bool:
        """Checks if there is an active internet connection."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except:
            return False
    
    def inner_message_parser(self, message: str) -> list[tuple[bool, str]]:
        message = message.split(utils.FILE_SEPARATOR)
        messages_list = []
        for i in range(len(message)):
            if i % 2 == 0:
                chunk = message[i].split(utils.MESSAGE_SEPARATOR)
                for line in chunk:
                    messages_list.append((False, line))
            else:
                messages_list.append((True, message[i].replace(' ', '')))
        return messages_list
        

    def message_parser(self, message: str) -> list[tuple[bool, str]]:
        message = message.split(utils.QUEUE_SEPARATOR)
        messages_list = []

        for i in range(len(message)):
            messages_list += self.inner_message_parser(message[i])
            if i < len(self.file_queue):
                messages_list.append((True, self.file_queue[i]))
        return messages_list

    def send_messages(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Sends WhatsApp messages to numbers listed in a DataFrame and returns a new DataFrame with the send status.

        Parameters:
            sheet (pd.DataFrame): DataFrame containing the columns "Numero" and "Mensagem".
                                  The "Numero" column should have phone numbers,
                                  and the "Mensagem" column should have the personalized messages for each number.

        Returns:
            pd.DataFrame: DataFrame containing the original columns and a new "Status" column
                          indicating whether the message was successfully sent or not.
        """

        def wait_whatsapp_end_loading(browser) -> None:
            """Waits for WhatsApp Web to fully load."""
            t: float = 0
            while len(browser.find_elements(By.ID, "side")) < 1 and t < utils.MAX_WAIT_TIME:
                time.sleep(1)
                t += 1
            time.sleep(5)  # Espera adicional para assegurar o carregamento

        def was_message_sent(browser) -> bool:
            """
            Checks if the message appears in the chat to confirm it was sent.
            This depends on WhatsApp UI changes.
            """
            try:
                sent_messages = browser.find_elements(By.CSS_SELECTOR, '.message-out')  # Outgoing message class
                return len(sent_messages) > 0
            except Exception:
                return False

        # Initialize the browser (Chrome, in this example)
        browser = webdriver.Chrome()
        status_list = []  # List to store the status of each send attempt

        for i, message in enumerate(sheet['Mensagem']):
            numero = sheet.loc[i, "Numero"]
            messages = self.message_parser(message)
            link = f"https://web.whatsapp.com/send?phone={numero}"

            # Check for internet connection before attempting to send a message
            # if not self.is_connected():
            #     status_list.append("Falha: Internet não disponível")
            #     print(f"Erro ao enviar mensagem para {numero}: Internet não disponível")
            #     continue

            try:
                browser.get(link)
                wait_whatsapp_end_loading(browser)
            except Exception as e:
                status_list.append("Falha")  # Caso ocorra algum erro
                print(f"Erro ao abrir o link do whatsapp para {numero}: {e}")
            
            try:
                if i == 1:
                    try:
                        browser.get(link)
                        wait_whatsapp_end_loading(browser)
                    except Exception as e:
                        status_list.append("Falha")  # Caso ocorra algum erro
                        print(f"Erro ao abrir o link do whatsapp para {numero}: {e}")
                for is_file, text in messages:
                    print(f"\t\t\t{is_file}: {text}")
                    if is_file:
                        WebDriverWait(browser, 2*utils.MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, utils.ATTACHMENTS_BUTTON))
                        ).click()
                        file_extension = text.split('.')
                        if len(file_extension) <= 1:
                            raise Exception("Invalid file path")
                        else:
                            file_extension = file_extension[-1]

                        if is_media(file_extension):
                            xpath = utils.MEDIA_XPATH
                        else:
                            xpath = utils.DOCS_XPATH

                        WebDriverWait(browser, 2*utils.MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, xpath))
                        ).send_keys(text)
                        WebDriverWait(browser, 2*utils.MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, utils.SEND_MEDIA_XPATH))
                        ).click()
                    else:
                        WebDriverWait(browser, 2*utils.MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, utils.XPATH_SEND_MESSAGE_FIELD))
                        ).send_keys(text)
                        WebDriverWait(browser, 2*utils.MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, utils.XPATH_SEND_MESSAGE_FIELD))
                        ).send_keys(Keys.ENTER)
                    time.sleep(utils.MESSAGE_DT)  # Aguarda para assegurar o envio da mensagem
                status_list.append("Sucesso")  # Se o envio foi bem-sucedido
            except Exception as e:
                # Check if the message might have been sent despite an exception
                if was_message_sent(browser):
                    status_list.append("Sucesso")
                else:
                    status_list.append(f"Falha: {str(e)}")
                print(f"Erro ao enviar mensagem para {numero}: {e}")

        # Close the browser after sending
        browser.quit()

        # Add the 'Status' column to the DataFrame
        sheet['Status'] = status_list
        return sheet

    def send_emails(self, sheet: pd.DataFrame) -> pd.DataFrame:
        # Initialize the browser (Chrome, in this example)
        status_list = []  # List to store the status of each send attempt

        context = ssl.create_default_context()

        for i, message in enumerate(sheet['Mensagem']):
            receiver = sheet.loc[i, "Email"]
            
            em = MIMEMultipart()
            em['From'] = self.sender_email
            em['To'] = receiver
            em['Subject'] = 'CASD'
            em.attach(MIMEText(message))

            # Check for internet connection before attempting to send a message
            if not self.is_connected():
                status_list.append("Falha: Internet não disponível")
                print(f"Erro ao enviar mensagem para {receiver}: Internet não disponível")
                continue
            
            for file_path in self.file_queue:
                with open(file_path, 'rb') as file:
                    name = file_path.split('/')[-1]
                    em.attach(MIMEApplication(file.read(), Name = name))

            with smtplib.SMTP_SSL('smtp.gmail.com', 465, context=context) as interface:
                try:
                    interface.login(self.sender_email, self.email_password)
                    interface.sendmail(self.sender_email, receiver, em.as_string())
                    status_list.append("Sucesso")  # Se o envio foi bem-sucedido
                except Exception as e:
                    # Check if the message might have been sent despite an exception
                    status_list.append(f"Falha: {str(e)}")
                    print(f"Erro ao enviar mensagem para {receiver}: {e}")

        # Add the 'Status' column to the DataFrame
        sheet['Status'] = status_list
        return sheet

    def generate_messages_from_template(self, sheet: pd.DataFrame, template: str, whatsapp_flag: bool) -> pd.DataFrame:
        """
        Gera mensagens personalizadas com base em um template e nos atributos de um DataFrame.

        Parâmetros:
            sheet (pd.DataFrame): Um DataFrame do Pandas contendo colunas como "Nome" e "Numero",
                                além de quaisquer outros atributos necessários para o template.
            template (str): Um texto modelo contendo placeholders (marcadores) que serão substituídos
                            pelos valores das colunas do DataFrame. Os placeholders devem corresponder
                            aos nomes das colunas em `sheet`, por exemplo, "{Nome}".
            whatsapp_flag (bool): Uma flaq que determina o meio de envio da mensagem, sendo:
                            0: WhatsApp
                            1: e-mail

        Retorna:
            pd.DataFrame: Um DataFrame do Pandas contendo as colunas "Nome", "Numero" e "Mensagem",
                        onde cada linha possui uma mensagem personalizada gerada para cada entrada.

        Exemplos:
            >>> data = pd.DataFrame({
            ...     "Nome": ["Alice", "Bob"],
            ...     "Numero": ["123456789", "987654321"],
            ...     "Cidade": ["São Paulo", "Rio de Janeiro"]
            ... })
            >>> template = "Olá, {Nome}! Como está o clima em {Cidade}?"
            >>> resultado = gerar_mensagens(None, data, template)
            >>> print(resultado)
                Nome     Numero                        Mensagem
            0   Alice  123456789   Olá, Alice! Como está o clima em São Paulo?
            1   Bob    987654321   Olá, Bob! Como está o clima em Rio de Janeiro?

        Observações:
            - Caso algum placeholder no template não corresponda a uma coluna no `sheet`, uma mensagem
            de erro será gerada para essa linha, e um aviso será exibido no console.
        """
        mensagens = []
        for _, row in sheet.iterrows():
            try:
                # Gera a mensagem formatando o template com os dados da linha
                mensagem = template.format(**row.to_dict())
                mensagens.append(mensagem)
            except KeyError as e:
                print(f"Aviso: Chave {e} não encontrada em uma linha do DataFrame.")
                mensagens.append("Erro ao gerar mensagem para esta linha.")

        # Verifica se as colunas necessárias estão presentes no DataFrame de saída
        if whatsapp_flag:
            required_field = "Numero"
        else:
            required_field = "Email"

        if "Nome" not in sheet.columns or required_field not in sheet.columns:
            raise ValueError(f"O DataFrame deve conter colunas 'Nome' e '{required_field}'.")

        # Retorna um DataFrame com as mensagens geradas
        return pd.DataFrame({
            "Nome": sheet["Nome"],
            required_field: sheet[required_field],
            "Mensagem": mensagens
        })
