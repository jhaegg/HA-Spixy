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

	def test_server_notice(self):
		tests = [
			':irc.example.com NOTICE AUTH :*** Looking up your hostname...'
		]

		expecteds = [
			('SERVER_NOTICE', {'target': "AUTH",
                               'host': "irc.example.com",
                               'message': "*** Looking up your hostname..."})
		]

		results = map(parse, tests)

		for expected, result in zip(expecteds, results):
			self.assertEqual(expected, result)