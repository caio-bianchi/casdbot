import pandas as pd
from src.bot import Bot
import pandas as pd

from src.bot import Bot


def test_generate_messages_from_template_whatsapp():
    bot = Bot()

    sheet = pd.DataFrame({'Nome': ['foo', 'bar'], 'Mensagem': ['test1', 'test2'], 'Numero': ['1', '2']})

    template = "olá {Nome}! {Mensagem}"

    mensagem = bot.generate_messages_from_template(sheet, template, True)

    assert mensagem['Mensagem'].to_list() == ['olá foo! test1', 'olá bar! test2']
    assert mensagem['Nome'].to_list() == ['foo', 'bar']
    assert mensagem['Numero'].to_list() == ['1', '2']

def test_generate_messages_from_template_email():
    bot = Bot()

    sheet = pd.DataFrame({'Nome': ['foo', 'bar'], 'Mensagem': ['test1', 'test2'], 'Email': ['foo@example.com', 'bar@example.com']})

    template = "olá {Nome}! {Mensagem}"

    mensagem = bot.generate_messages_from_template(sheet, template, False)

    assert mensagem['Mensagem'].to_list() == ['olá foo! test1', 'olá bar! test2']
    assert mensagem['Nome'].to_list() == ['foo', 'bar']
    assert mensagem['Email'].to_list() == ['foo@example.com', 'bar@example.com']

def test_generate_messages_from_template_when_there_is_no_match_in_arguments_from_template():
    bot = Bot()

    sheet = pd.DataFrame({'Nome': ['foo'], 'Mensagem': ['test1'], 'Numero': ['1'], 'test': ['test1']})

    template = "olá {Nome}! {Mensagem} {Idade}"

    mensagem = bot.generate_messages_from_template(sheet, template, True)

    assert mensagem['Mensagem'].to_list() == ['Erro ao gerar mensagem para esta linha.']

def test_generate_messages_from_template_when_required_columns_are_missing():
    bot = Bot()

    sheet = pd.DataFrame({'Mensagem': ['test1', 'test2'], 'Idade': ['1', '2']})

    template = "olá {Nome}! {Mensagem} {Idade}"

    try:
        bot.generate_messages_from_template(sheet, template, True)
    except ValueError as e:
        assert str(e) == "O DataFrame deve conter colunas 'Nome' e 'Numero'."