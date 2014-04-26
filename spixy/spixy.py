from gevent.monkey import patch_all
patch_all()

from gevent import Greenlet

from json import load

from irc.client import Client

class RawSender(Greenlet):
	def __init__(self, client):
		Greenlet.__init__(self)
		self.client = client

	def _run(self):
		command = ''
		while command != '/quit':
			command = input_raw('>:')
			client._send_raw(command)


if __name__ == '__main__':
	with open('config/spixy.json') as:
		config = load(f)

	client = Client(**config)
	console = RawSender(client)
	client.connect()
	console.start()
	console.join()
	client.close()
