from unittest.mock import patch, MagicMock

import pandas as pd

from src.bot import Bot


def test_send_messages():
    bot = Bot()

    bot.is_connected = MagicMock(return_value=True)

    sheet = pd.DataFrame({
        'Numero': ['1234567890', '0987654321'],
        'Mensagem': ['Olá, número 1!', 'Olá, número 2!']
    })

    with patch('selenium.webdriver.Chrome') as mock_browser:
        browser_instance = mock_browser.return_value
        browser_instance.get.return_value = None
        browser_instance.find_elements.return_value = [MagicMock()]

        browser_instance.find_element.return_value = MagicMock()

        result = bot.send_messages(sheet)

        assert result['Status'].to_list() == ['Sucesso', 'Sucesso']

def test_send_messages_no_internet():
    bot = Bot()

    bot.is_connected = MagicMock(return_value=False)

    sheet = pd.DataFrame({
        'Numero': ['1234567890'],
        'Mensagem': ['Olá, número sem internet!']
    })

    result = bot.send_messages(sheet)

    assert result['Status'].to_list() == ['Falha: Internet não disponível']

def test_send_messages_empty_sheet():
    bot = Bot()

    bot.is_connected = MagicMock(return_value=True)

    sheet = pd.DataFrame(columns=['Numero', 'Mensagem'])

    result = bot.send_messages(sheet)

    assert result.empty
