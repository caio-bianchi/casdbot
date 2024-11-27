from unittest.mock import patch, MagicMock

import pandas as pd

from src.bot import Bot


def test_send_emails():
    bot = Bot()
    bot.is_connected = MagicMock(return_value=True)

    sheet = pd.DataFrame({
        'Nome': ['foo', 'bar'],
        'Email': ['foo@example.com', 'bar@example.com'],
        'Mensagem': ['Olá, foo!', 'Olá, bar!']
    })

    with patch('smtplib.SMTP_SSL') as mock_smtp:
        smtp_instance = mock_smtp.return_value
        smtp_instance.login.return_value = None
        smtp_instance.sendmail.return_value = None

        result = bot.send_emails(sheet)

        assert result['Status'].to_list() == ['Sucesso', 'Sucesso']

def test_send_emails_no_internet():
    bot = Bot(sender_email='foo@example.com', email_password='<PASSWORD>')

    bot.is_connected = MagicMock(return_value=False) # Simula a falta de conexão

    sheet = pd.DataFrame({
        'Nome': ['foo'],
        'Email': ['foo@example.com'],
        'Mensagem': ['Olá, foo!']
    })

    result = bot.send_emails(sheet)

    assert result['Status'].to_list() == ['Falha: Internet não disponível']

def test_send_emails_with_attachments():
    bot = Bot(sender_email='foo@example.com', email_password='<PASSWORD>')

    bot.is_connected = MagicMock(return_value=True)

    # Necessario criar um stub .txt sem nada
    bot.add_to_queue("test_file.txt")

    sheet = pd.DataFrame({
        'Nome': ['foo'],
        'Email': ['foo@example.com'],
        'Mensagem': ['Olá, foo!']
    })

    with patch('smtplib.SMTP_SSL') as mock_smtp:
        smtp_instance = mock_smtp.return_value
        smtp_instance.login.return_value = None
        smtp_instance.sendmail.return_value = None

        result = bot.send_emails(sheet)

        assert result['Status'].to_list() == ['Sucesso']


def test_send_emails_empty_sheet():
    bot = Bot(sender_email='foo@example.com', email_password='<PASSWORD>')

    bot.is_connected = MagicMock(return_value=True)

    sheet = pd.DataFrame(columns=['Nome', 'Email', 'Mensagem'])

    result = bot.send_emails(sheet)

    assert result.empty