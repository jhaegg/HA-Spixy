import utils.format_parse as format_parse

_events = {'PING': 'PING :{{timestamp:[0-9]*}}'}

events = _events.keys()

def valid_event(event):
	return event.upper() in events

def parse(string):
	#  Want to do this with any(map(lambda)) >:|
	for event, fmt in _events:
		res = format_parse.parse(fmt, string)
		if res:
			return event, res