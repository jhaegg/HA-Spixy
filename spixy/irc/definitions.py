import spixy.utils.format_parse as format_parse

_host = "{{host:[0-9a-zA-Z\.\-:]+}}"
_nick_valid = "0-9a-zA-Z\-_´`"
_chan_valid = "#\%"
_nick = "{{nick:[" + _nick_valid + "]+}}"
_target = "{{target:[" + _nick_valid + _chan_valid + "]+}}"
_ident = "{{ident:~?[0-9a-zA-Z]+}}"
_fulluser = _nick + "!" + _ident + "@" + _host
_message_part = " :{{message:.*}}"

_events = {'PING': "PING :{{timestamp:[0-9a-zA-Z\.\-:]+}}",
           'SERVER_NOTICE': ":" + _host + " NOTICE " + _target + _message_part,
           'BLANK_NOTICE': "NOTICE " + _target + _message_part,
           'NOTICE': ":" + _fulluser + " NOTICE " + _target + _message_part,
           'REPLY': ":" + _host + " {{code:[0-9]{2}[0-9]}} " + _target + _message_part,
           'PRIVMSG': ":" + _fulluser + " PRIVMSG " + _target + _message_part}

events = _events.keys()


def valid_event(event):
    return event.upper() in events


def parse(string):
    for event, fmt in _events.items():
        res = format_parse.parse(fmt, string)
        if res is not None:
            return event, res

    return None, None
