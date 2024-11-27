from src.bot import Bot

def test_message_parser():
    bot = Bot()

    bot.file_queue = ["foo", "bar"]

    s = "test1 [break] test2 [file] /foo/bar/baz.png [file] test3 [queue] test4 [queue] test5"

    s = bot.message_parser(message=s)

    assert s == [
        (False, 'test1 '),
        (False, ' test2 '),
        (True, '/foo/bar/baz.png'),
        (False, ' test3 '),
        (True, 'foo'),
        (False, ' test4 '),
        (True, 'bar'),
        (False, ' test5'),
    ]