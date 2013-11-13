import socket

import definitions


class Client():
	def __init__(self, host, user, port=6669):
		self.host = host
		self.port = port
		self.user = user
		self.listeners = {event: [] for event in definitions.events}

	def connect(self):
		self.register_listener('PING', self._pong)
		self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
		self.socket.connect((self.host, self.port))
		self._send_raw('NICK %s' % self.user)
		# Spawn gevent coroutine for handling events
		

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