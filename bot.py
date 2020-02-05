import telegram
import logging
from telegram.ext import Updater
from telegram.ext import CommandHandler
import requests
import json
import datetime
import os
import matplotlib.pyplot as plt

TOKEN = '849622134:AAHi8k4ovnrVorRru1ivjS8xlu4CKggAb_Y'
# data base file
FILE = 'data.txt'
# minutes for difference in base
TIME_DIFF = 10
# graph file name
PLOT_FILENAME = 'graph.png'

def get_data_from_api():
	"""
		Get data from Api and save it to base
	"""
	# get data from api and convert it
	response = requests.get('https://api.exchangeratesapi.io/latest?base=USD')
	content = json.loads(response.content).get('rates')

	date = datetime.datetime.now().strftime("%m/%d/%Y, %H:%M:%S") + '\n'

	# formatting data and write it
	message = ''
	for key, value in content.items():
		message += key + ': ' + str(round(value, 2)) + '\n'

	with open(FILE, 'w') as file:
		file.write(date)
		file.write(message)

	return message


def get_data_from_file():
	"""
		Read data from file, if it need
	"""
	with open(FILE, 'r') as file:
		file.readline()

		content = file.read().strip()

	return content


def get_data():
	"""
		Get data from API with params
	"""
	with open(FILE, 'r') as file:
		date = file.readline().strip()

	try:
		date = datetime.datetime.strptime(date, "%m/%d/%Y, %H:%M:%S")
	except:
		date = datetime.datetime.min
	finally:
		diff = (datetime.datetime.now() - date).total_seconds()

	if diff / 60 < TIME_DIFF:
		message = get_data_from_file()
	else:
		message = get_data_from_api()

	return message


def exchange_data(context):
	"""
		Get data from api or base and convert in for exchange fuc
	"""
	if context[0][0] == '$' and len(context) == 3:
		convert = context[2]
		count = context[0][1:]
	elif context[0][0] != '$' and context[1] == 'USD' and len(context) == 4:
		convert = context[3]
		count = context[0]
	
	data = get_data()
	data = data.split('\n')
	data = {item.split(': ')[0]: item.split(': ')[1] for item in data}

	try:
		result = float(count) * float(data[convert])
	except:
		return 'Error in data! Need to be like "$10 to CAD"'

	message = '$' + str(round(result, 2))
	return message

def create_history_plot(data):
	"""
		Create graph for history
	"""
	x, y = [], []
	for item in data:
		x.append(item)
		y.append(list(data[item].values())[0])
	if not x or not y:
		return 'No exchange rate data is available for the selected currency.'
	plt.plot(x, y)
	plt.savefig(PLOT_FILENAME)
	return 'Done'


def get_history(context):
	"""
		Get history from api for history func
	"""

	# split all context to data
	base, symbols = context[0].split('/')
	try:
		days = int(context[2])
	except:
		return 'Error in data! Need to be like "USD/CAD for 7 days"'

	# create data for api
	start_at = datetime.datetime.now().date() - datetime.timedelta(days=days)
	end_at = datetime.datetime.now().date()

	start_at = start_at.strftime("%Y-%m-%d")
	end_at = end_at.strftime("%Y-%m-%d")

	url = 'https://api.exchangeratesapi.io/history?start_at={}&end_at={}&base={}&symbols={}'.format(start_at, end_at, base, symbols)
	
	response = requests.get(url)
	if response.status_code != 200:
		return 'Error in data! Need to be like "USD/CAD for 7 days"'

	data = json.loads(response.content)
	
	message = create_history_plot(data['rates'])
	return message


def start(update, context):
	message = """
	Check commands: /list, /exchange, /history
	"""
	context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def lst(update, context):

	message = get_data()

	context.bot.send_message(chat_id=update.effective_chat.id, text=message)


def exchange(update, context):
	"""
		Convert money
	"""

	if context.args:
		message = exchange_data(context.args)
	else:
		message = 'Error in data! Need to be like "$10 to CAD"'

	context.bot.send_message(chat_id=update.effective_chat.id, text=message)

def history(update, context):
	"""
	Take a history from API, create plot and send in to Bot.
	"""

	if context.args:
		message = get_history(context.args)
		context.bot.send_photo(chat_id=update.effective_chat.id, photo=open(PLOT_FILENAME, 'rb'))

	else:
		message = 'Error in data! Need to be like "USD/CAD for 7 days"'
		context.bot.send_message(chat_id=update.effective_chat.id, text=message)

	os.remove(PLOT_FILENAME)



def main():
	# create db file if not excist
	with open(FILE, 'a') as file:
		pass

	updater = Updater(TOKEN, use_context=True)

	updater.dispatcher.add_handler(CommandHandler('start', start))
	updater.dispatcher.add_handler(CommandHandler(('list', 'lst'), lst))
	updater.dispatcher.add_handler(CommandHandler('exchange', exchange))
	updater.dispatcher.add_handler(CommandHandler('history', history))

    # Start the Bot
	print('Working..')
	updater.start_polling()



if __name__ == '__main__':
    main()
