from gevent.monkey import patch_all
patch_all()

import socket
from definitions import valid_event, parse
from logging import getLogger

logger = getLogger(__name__)

__all__ = ['Client']


class EventHandler(Greenlet):
	def __init__(self, client):
		Greenlet.__init__(self)
		self.client = client
		self.shutdown = False

	def _run(self):
		while(not self.shutdown):
			message = self.client.socket.recv(4096)
			event, parameters = parse(message)

			if event is None:
				logger.Error('Unparsable event %s' % message)
			else:
				map(self.client.listeners[event], **event)

	def close(self):
		self.shutdown = True


class Client():
	def __init__(self, host, user, port=6669):
		self.host = host
		self.port = port
		self.user = user
		self.listeners = {event: [] for event in definitions.events}

	def __repr__(self):
		return 'Client(host=%s, port=%d, user=%s)' % (self.host, self.port, self.user)

	def connect(self):
		self.register_listener('PING', self._pong)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))
		self._send_raw('NICK %s' % self.user)
		self.event_handler = EventHandler(self)
		self.event_handler.start()

	def close():
		if hasattr(self, 'event_handler'):
			self.event_handler.close()
			self.event_handler.join()

		if hasattr(self, 'socket'):
			self._send_raw('QUIT :exiting')
			self.socket.close()

	def register_listener(self, event, listener):
		if definitions.valid_event(event):
			self.listeners[event].append(listener)
		else:
			raise TypeError('Invalid IRC event %s.' % event)

	def _send_raw(self, string):
		self.socket.sendall('%s\n' % string)

	#  Default event handlers

	def _pong(self, timestamp):
		self._send_raw('PONG %d' % timestamp)
