from structures import *
import pandas as pd
import urllib.parse

from selenium import webdriver # Abrir navegador
from selenium.webdriver.common.keys import Keys # Enviar as mensagens
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
import time
import urllib
import socket

MESSAGE_DT = 12
XPATH_SEND_MESSAGE_FIELD = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div/p'
ADDITIONAL_TOOLS_FIELD = '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/div/div/div/span'
ATTACHMENTS_BUTTON = '//*[@id="main"]/footer/div[1]/div/span/div/div[1]/div[2]/button'
MEDIA_XPATH = '//input[@accept="image/*,video/mp4,video/3gpp,video/quicktime"]'
DOCS_XPATH  = '//input[@accept="*"]'
SEND_MEDIA_XPATH = '//*[@id="app"]/div/div[3]/div[2]/div[2]/span/div/div/div/div[2]/div/div[2]/div[2]/div/div'
MESSAGE_SEPARATOR = '[break]'
FILE_SEPARATOR = '[file]'
QUEUE_SEPARATOR = '[queue]'


class Bot:
    def __init__(self):
        self.file_queue = []
        pass

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
        message = message.split(FILE_SEPARATOR)
        messages_list = []
        for i in range(len(message)):
            if i % 2 == 0:
                chunk = message[i].split(MESSAGE_SEPARATOR)
                for line in chunk:
                    messages_list.append((False, line))
            else:
                messages_list.append((True, message[i].replace(' ', '')))
        return messages_list
        

    def message_parser(self, message: str) -> list[tuple[bool, str]]:
        message = message.split(QUEUE_SEPARATOR)
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
            while len(browser.find_elements(By.ID, "side")) < 1:
                time.sleep(1)
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
            if not self.is_connected():
                status_list.append("Falha: Internet não disponível")
                print(f"Erro ao enviar mensagem para {numero}: Internet não disponível")
                continue

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
                        WebDriverWait(browser, 2*MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, ATTACHMENTS_BUTTON))
                        ).click()
                        WebDriverWait(browser, 2*MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, MEDIA_XPATH))
                        ).send_keys(text)
                        WebDriverWait(browser, 2*MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, SEND_MEDIA_XPATH))
                        ).click()
                    else:
                        WebDriverWait(browser, 2*MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, XPATH_SEND_MESSAGE_FIELD))
                        ).send_keys(text)
                        WebDriverWait(browser, 2*MESSAGE_DT).until(
                            EC.presence_of_element_located((By.XPATH, XPATH_SEND_MESSAGE_FIELD))
                        ).send_keys(Keys.ENTER)
                    time.sleep(MESSAGE_DT)  # Aguarda para assegurar o envio da mensagem
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

    def generate_messages_from_template(self, sheet: pd.DataFrame, template: str) -> pd.DataFrame:
        """
        Gera mensagens personalizadas com base em um template e nos atributos de um DataFrame.

        Parâmetros:
            sheet (pd.DataFrame): Um DataFrame do Pandas contendo colunas como "Nome" e "Numero",
                                além de quaisquer outros atributos necessários para o template.
            template (str): Um texto modelo contendo placeholders (marcadores) que serão substituídos
                            pelos valores das colunas do DataFrame. Os placeholders devem corresponder
                            aos nomes das colunas em `sheet`, por exemplo, "{Nome}".

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
        if "Nome" not in sheet.columns or "Numero" not in sheet.columns:
            raise ValueError("O DataFrame deve conter colunas 'Nome' e 'Numero'.")

        # Retorna um DataFrame com as mensagens geradas
        return pd.DataFrame({
            "Nome": sheet["Nome"],
            "Numero": sheet["Numero"],
            "Mensagem": mensagens
        })
