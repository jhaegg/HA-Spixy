_actions = {'PING': 'PING :{timestamp:[0-9]*}'}

actions = _actions.keys()

def valid_action(action):
	return action.upper() in actions

def parse(str):
	pass