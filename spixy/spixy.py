import time

from irc.client import Client


if __name__ == '__main__':
	client = Client()
	client.connect()
	time.sleep(60)