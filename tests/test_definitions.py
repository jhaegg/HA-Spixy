import unittest
from spixy.irc.definitions import parse


class TestDefinitions(unittest.TestCase):
    def test_ping(self):
        tests = [
            "PING :123",
            "PING :abc"
        ]

        expecteds = [
            ('PING', {'timestamp': '123'}),
            (None, None)
        ]

        results = map(parse, tests)

        for result, expected in zip(results, expecteds):
            self.assertEqual(result, expected)

    def test_notice(self):
        tests = [
            ':irc.example.com NOTICE AUTH :*** Looking up your hostname...',
            ':Vargpack!vargpack@feed:babe:dead:beef NOTICE #chan :wololo'
        ]

        expecteds = [
            ('SERVER_NOTICE', {'target': "AUTH",
                               'host': "irc.example.com",
                               'message': "*** Looking up your hostname..."}),
            ('NOTICE', {'target': '#chan',
                        'nick': 'Vargpack',
                        'ident': 'vargpack',
                        'host': 'feed:babe:dead:beef',
                        'message': 'wololo'})
        ]

        results = map(parse, tests)

        for expected, result in zip(expecteds, results):
            self.assertEqual(expected, result)

    def test_reply(self):
        tests = [
            ':irc.example.com 001 User :Welcome to the IRC test User'
        ]

        expecteds = [
            ('REPLY', {'target': "User",
                       'host': "irc.example.com",
                       'code': "001",
                       'message': "Welcome to the IRC test User"})
        ]

        results = map(parse, tests)

        for expected, result in zip(expecteds, results):
            self.assertEqual(expected, result)
