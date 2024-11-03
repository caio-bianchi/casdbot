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

TIME_TO_WAIT_MESSAGE_TO_BE_SENT = 10

class Bot:
    def __init__(self):
        pass

    def send_messages(self, sheet: pd.DataFrame):

        def wait_whatsapp_end_loading(browser)->None:
            while len(browser.find_elements(By.ID,"side")) < 1:
                time.sleep(1)
            time.sleep(2)

        browser = webdriver.Chrome()
        for i, message in enumerate(sheet['Mensagem']):
            numero = sheet.loc[i, "Numero"]
            texto = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"
            browser.get(link)

            wait_whatsapp_end_loading(browser)

            xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div/p' # xpath do campo para apertar enter
            browser.find_element(By.XPATH, xpath).send_keys(Keys.ENTER) # Apertar ENTER

            time.sleep(TIME_TO_WAIT_MESSAGE_TO_BE_SENT)

    def gerar_mensagens(self, sheet: pd.DataFrame, template: str) -> pd.DataFrame:
        mensagens = []
        for _, row in sheet.iterrows():
            try:
                mensagem = template.format(**row.to_dict())
                mensagens.append(mensagem)
            except KeyError as e:
                print(f"Aviso: Chave {e} não encontrada em uma linha do DataFrame.")
                mensagens.append("Erro ao gerar mensagem para esta linha.")
        
        # Return a DataFrame with the messages
        return pd.DataFrame({"Nome": sheet["Nome"], "Numero": sheet["Numero"], "Mensagem": mensagens})