import unittest
import spixy.utils.format_parse as format_parse

class TestFormatParse(unittest.TestCase):
	def test_format_single(self):
		format = 'Spam {{spam:sp[aA]*m}}'
		tests = [
			'Spam spam',
			'Spam spAm',
			'Spam spAam',
			'Spam ham',
			'Spam sPam'
		]

		expecteds = [
			{'spam': 'spam'},
			{'spam': 'spAm'},
			{'spam': 'spAam'},
			{},
			{}
		]

		results = [format_parse.parse(format, test) for test in tests]

		for result, expected in zip(results, expecteds):
			self.assertEqual(result, expected)
