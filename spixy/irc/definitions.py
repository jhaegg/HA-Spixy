import spixy.utils.format_parse as format_parse

_host = "{{host:[0-9a-zA-Z\.\-:]+}}"
_fulluser = "{{nick:[0-9a-zA-Z]+}}!{{ident:[0-9a-zA-Z]+}}@" + _host


_events = {'PING': "PING :{{timestamp:[0-9]+}}",
           'SERVER_NOTICE': ":" + _host  + " NOTICE {{target:[0-9a-zA-Z\-]+}} :{{message:.*}}",
           'NOTICE': ":" + _fulluser + " NOTICE {{target:[#0-9a-zA-Z\-]+}} :{{message:.*}}"}

events = _events.keys()

def valid_event(event):
	return event.upper() in events

def parse(string):
	for event, fmt in _events.items():
		res = format_parse.parse(fmt, string)
		if res is not None:
			return event, res

	return None, None
