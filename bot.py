from structures import *
import pandas as pd
import urllib.parse

from selenium import webdriver # Abrir navegador
from selenium.webdriver.common.keys import Keys # Enviar as mensagens
from selenium.webdriver.common.by import By
import time
import urllib
import socket

TIME_TO_WAIT_MESSAGE_TO_BE_SENT = 10
XPATH_SEND_MESSAGE_FIELD = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div/p'


class Bot:
    def __init__(self):
        pass

    def is_connected(self) -> bool:
        """Checks if there is an active internet connection."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

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
            time.sleep(2)  # Additional wait to ensure loading is complete

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
            texto = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"

            # Check for internet connection before attempting to send a message
            if not self.is_connected():
                status_list.append("Falha: Internet não disponível")
                print(f"Erro ao enviar mensagem para {numero}: Internet não disponível")
                continue

            try:
                browser.get(link)
                wait_whatsapp_end_loading(browser)

                # Check again for internet connection after loading the page
                if not self.is_connected():
                    status_list.append("Falha: Internet não disponível durante envio")
                    print(f"Erro ao enviar mensagem para {numero}: Internet não disponível durante envio")
                    continue

                # Send the message
                browser.find_element(By.XPATH, XPATH_SEND_MESSAGE_FIELD).send_keys(Keys.ENTER)
                time.sleep(TIME_TO_WAIT_MESSAGE_TO_BE_SENT)  # Ensure the message is sent

                # Confirm if the message was actually sent
                if was_message_sent(browser):
                    status_list.append("Sucesso")
                else:
                    status_list.append("Falha: Mensagem não enviada")
                    print(f"Erro ao enviar mensagem para {numero}: Mensagem não confirmada")

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