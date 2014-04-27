from codecs import getdecoder
from curses import ascii
from threading import Thread
from logging import getLogger
import socket
from time import sleep

from spixy.irc.definitions import valid_event, parse, events


logger = getLogger(__name__)

__all__ = ['Client']


class EventHandler(Thread):
	def __init__(self, client):
		Thread.__init__(self)
		self.client = client
		self.shutdown = False

	def run(self):
		utf8decoder = getdecoder('utf-8')
		latin1decoder = getdecoder('latin-1')

		while(not self.shutdown):
			data = self.client.socket.recv(4096)
			datalen = len(data)
			if datalen > 0:
				try:
					(message, decoded) = utf8decoder(data)
				except (UnicodeDecodeError, UnicodeTranslateError):
					(message, decoded) = latin1decoder(data)

				if datalen != decoded:
					logger.warning('Not all bytes decoded: %r' % data)

				message = message.rstrip()

				logger.info("Message: %r" % message)
				event, parameters = parse(message)

				if event is None:
					logger.error("Unparsable message %s" % message)
				else:
					for listener in self.client.listeners[event]:
						listener(**parameters)
			else:
				sleep(0.5)


	def close(self):
		self.shutdown = True


class Client():
	def __init__(self, host, port, user, nick, name):
		self.host = host
		self.port = port
		self.user = user
		self.nick = nick
		self.name = name
		self.listeners = {event: [] for event in events}

	def __repr__(self):
		return 'Client(host=%s, port=%d, user=%s)' % (self.host, self.port, self.user)

	def connect(self):
		self.register_listener('PING', self._pong)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))
		self._send_raw('PASS')
		self._send_raw('NICK %s' % self.nick)
		self._send_raw('USER %s 0 * :%s' % (self.user, self.name))
		self.event_handler = EventHandler(self)
		self.event_handler.start()

	def close(self):
		if hasattr(self, 'socket'):
			self._send_raw('QUIT :Exiting')
			self.socket.close()

		if hasattr(self, 'event_handler'):
			self.event_handler.close()
			self.event_handler.join()

	def register_listener(self, event, listener):
		if valid_event(event):
			self.listeners[event].append(listener)
		else:
			raise TypeError('Invalid IRC event %s.' % event)

	def _send_raw(self, string):
		self.socket.sendall(str.encode('%s\r\n' % string))

	#  Default event handlers

	def _pong(self, timestamp):
		self._send_raw('PONG %s' % timestamp)
