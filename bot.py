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

class Bot:
    def __init__(self):
        pass

    def send_messages(self, sheet: pd.DataFrame):

        def whatsapp_end_loading(browser)->bool:
            return len(browser.find_elements(By.ID,"side")) < 1

        browser = webdriver.Chrome()
        for i, message in enumerate(sheet['Mensagem']):
            nome = sheet.loc[i, "Nome"]
            numero = sheet.loc[i, "Numero"]
            texto = urllib.parse.quote(message)
            link = f"https://web.whatsapp.com/send?phone={numero}&text={texto}"
            browser.get(link)

            while whatsapp_end_loading(browser):
                time.sleep(1)
            time.sleep(2)

            xpath = '//*[@id="main"]/footer/div[1]/div/span/div/div[2]/div[1]/div/div/p' # xpath do campo para apertar enter
            browser.find_element(By.XPATH, xpath).send_keys(Keys.ENTER) # Apertar ENTER

            time.sleep(10)