# -*- coding: utf8 -*-

import spixy.utils.format_parse as format_parse

_host = r"{{host:[0-9a-zA-Z\.\-:]+}}"
_nick_valid = r"0-9a-zA-Z\-_´`"
_chan_valid = r"#\%"
_nick = r"{{nick:[" + _nick_valid + r"]+}}"
_target = r"{{target:[" + _nick_valid + _chan_valid + r"]+}}"
_ident = r"{{ident:~?[0-9a-zA-Z\.]+}}"
_fulluser = _nick + r"!" + _ident + r"@" + _host
_message_part = r" :{{message:.*}}"

_events = {r'PING': r"PING :{{timestamp:[0-9a-zA-Z\.\-:]+}}",
           r'SERVER_NOTICE': r":" + _host + r" NOTICE " + _target + _message_part,
           r'BLANK_NOTICE': r"NOTICE " + _target + _message_part,
           r'NOTICE': ":" + _fulluser + " NOTICE " + _target + _message_part,
           r'REPLY': ":" + _host + r" {{code:[0-9]{2}[0-9]}} " + _target + _message_part,
           r'PRIVMSG': ":" + _fulluser + r" PRIVMSG " + _target + _message_part}

events = _events.keys()


def valid_event(event):
    return event.upper() in events


def parse(string):
    for event, fmt in _events.items():
        res = format_parse.parse(fmt, string)
        if res is not None:
            return event, res

    return None, None
