import spixy.utils.format_parse as format_parse

_events = {'PING': 'PING :{{timestamp:[0-9]*}}'}

events = _events.keys()

def valid_event(event):
	return event.upper() in events

def parse(string):
	for event, fmt in _events.items():
		res = format_parse.parse(fmt, string)
		if res is not None:
			return event, res

	return None, None
