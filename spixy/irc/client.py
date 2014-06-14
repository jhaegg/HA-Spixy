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

        while (not self.shutdown):
            data = self.client.socket.recv(4096)
            datalen = len(data)
            if datalen > 0:
                try:
                    (message, decoded) = utf8decoder(data)
                except (UnicodeDecodeError, UnicodeTranslateError):
                    (message, decoded) = latin1decoder(data)

                if datalen != decoded:
                    logger.warning('Not all bytes decoded: %r' % data)

                for line in [l.strip() for l in message.split('\n') if l]:
                    event, parameters = parse(line)

                    if event is None:
                        logger.error("Could not parse %r" % line)
                    else:
                        for listener in self.client.listeners[event]:
                            try:
                                listener(**parameters)
                            except:
                                logger.exception("Uncaught exception in event listener on message:\n%s" % line)
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
        self.register_listener('SERVER_NOTICE', self._auth_login)
        self.register_listener('BLANK_NOTICE', self._auth_login)
        self.socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket.connect((self.host, self.port))
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

    def remove_listener(self, event, listener):
        if valid_event(event):
            self.listeners[event].remove(listener)
        else:
            raise TypeError('Invalid IRC event %s.' % event)

    def _send_raw(self, string):
        self.socket.sendall(str.encode('%s\r\n' % string))

    # IRC messages

    def privmsg(self, target, message):
        self._send_raw("PRIVMSG {target} :{message}".format(target=target, message=message))

    # Default event handlers

    def _pong(self, timestamp):
        self._send_raw('PONG %s' % timestamp)

    def _auth_login(self, target, **kwargs):
        if target == 'AUTH':
            self._send_raw('NICK %s' % self.nick)
            self._send_raw('USER %s 0 * :%s' % (self.user, self.name))
            self.remove_listener('SERVER_NOTICE', self._auth_login)
            self.remove_listener('BLANK_NOTICE', self._auth_login)
