import unittest

import bot

class TestStringMethods(unittest.TestCase):

	def setUp(self):
		data = bot.get_data()
		data = data.split('\n')
		self.data = {item.split(': ')[0]: item.split(': ')[1] for item in data}

	def test_true_convert_data(self):
		a = ['$10', 'to', 'CAD']

		res = bot.convert(a)
		true = '$' + str(float(self.data['CAD']) * 10)
		self.assertEqual(res, true)

		a = ['10', 'USD', 'to', 'CAD']
		res = bot.convert(a)
		self.assertEqual(res, true)

	def test_error_convert_data(self):
		true = 'Error in data! Need to be like "$10 to CAD"'

		a = ['10', 'to', 'CAD']
		res = bot.convert(a)
		self.assertEqual(res, true)

		a = ['10',  'CAD']
		res = bot.convert(a)
		self.assertEqual(res, true)

		a = ['$10', 'to', 'zzz']
		res = bot.convert(a)
		self.assertEqual(res, true)

		a = ['10', 'USDs', 'to', 'CAD']
		res = bot.convert(a)
		self.assertEqual(res, true)

		a = ['$10', 'USD', 'to', 'CAD']
		res = bot.convert(a)
		self.assertEqual(res, true)

		a = ['10', 'USD', 'to', 'zzz']
		res = bot.convert(a)
		self.assertEqual(res, true)

		a = ['10', 'USD', 'zzz']
		res = bot.convert(a)
		self.assertEqual(res, true)


if __name__ == '__main__':
	unittest.main()