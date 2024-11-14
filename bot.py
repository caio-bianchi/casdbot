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

    def is_connected(self):
        """Checks if there is an active internet connection."""
        try:
            socket.create_connection(("8.8.8.8", 53), timeout=2)
            return True
        except OSError:
            return False

    def send_messages(self, sheet: pd.DataFrame) -> pd.DataFrame:
        """
        Envia mensagens de WhatsApp para números listados em um DataFrame e retorna um novo DataFrame com o status do envio.

        Parâmetros:
            sheet (pd.DataFrame): DataFrame contendo as colunas "Numero" e "Mensagem".
                                A coluna "Numero" deve conter os números de telefone e
                                a coluna "Mensagem" as mensagens personalizadas para cada número.

        Retorna:
            pd.DataFrame: DataFrame contendo as colunas originais e uma nova coluna "Status", indicando
                        se a mensagem foi enviada com sucesso ou não.
        """

        def wait_whatsapp_end_loading(browser) -> None:
            """ Aguarda o carregamento completo do WhatsApp Web """
            while len(browser.find_elements(By.ID, "side")) < 1:
                time.sleep(1)
            time.sleep(2)  # Espera adicional para assegurar o carregamento

        # Inicializa o navegador (Chrome, neste exemplo)
        browser = webdriver.Chrome()
        status_list = []  # Lista para armazenar o status de cada envio

        for i, message in enumerate(sheet['Mensagem']):
            numero = sheet.loc[i, "Numero"]
            texto = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"

            # Check for internet connection
            if not self.is_connected():
                status_list.append("Falha: Internet não disponível")
                print(f"Erro ao enviar mensagem para {numero}: Internet não disponível")
                continue

            try:
                browser.get(link)
                wait_whatsapp_end_loading(browser)
                browser.find_element(By.XPATH, XPATH_SEND_MESSAGE_FIELD).send_keys(Keys.ENTER)
                time.sleep(TIME_TO_WAIT_MESSAGE_TO_BE_SENT)  # Aguarda para assegurar o envio da mensagem
                if not self.is_connected():
                    status_list.append("Falha: Internet não disponível")
                    continue
                status_list.append("Sucesso")  # Se o envio foi bem-sucedido

            except Exception as e:
                status_list.append("Falha")  # Caso ocorra algum erro
                print(f"Erro ao enviar mensagem para {numero}: {e}")

        # Fecha o navegador após o envio
        browser.quit()

        # Adiciona a coluna 'Status' ao DataFrame
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