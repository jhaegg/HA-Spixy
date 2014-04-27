from json import load
from threading import Thread

from spixy.irc.client import Client

class RawSender(Thread):
	def __init__(self, client):
		Thread.__init__(self)
		self.client = client

	def run(self):
		command = ''
		while command != '/quit':
			command = input('>:')
			client._send_raw(command)


if __name__ == '__main__':
	with open('config/spixy.json') as f:
		config = load(f)

	client = Client(**config)
	console = RawSender(client)
	client.connect()
	console.start()
	console.join()
	client.close()
