import definitions


class Client():
	def __init__(self, host, user, port=6669):
		self.host = host
		self.port = port
		self.user = user
		self.listeners = {action: [] for action in definitions.actions}

	def connect(self):
		pass

	def register_listener(self, action, listener):
		if definitions.valid_action(action):
			self.listeners[action] += listener
		else:
			raise TypeError('Invalid IRC action %s.' % action)