import asyncio
import logging

from codecs import getdecoder

from spixy.irc.definitions import valid_event, parse, events


logger = logging.getLogger(__name__)
logger.setLevel(logging.ERROR)
_ch = logging.StreamHandler()
_ch.setLevel(logging.ERROR)
_ch.setFormatter(logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s'))
logger.addHandler(_ch)


class Client():
    def __init__(self, host, port, user, nick, name):
        self._host = host
        self._port = port
        self._user = user
        self._nick = nick
        self._name = name
        self._decoders = [getdecoder('utf-8'), getdecoder('latin-1')]

        self._listeners = {event: [] for event in events}

    def register_listener(self, event, listener):
        if valid_event(event):
            self._listeners[event].append(listener)
        else:
            raise TypeError('Invalid IRC event %s.' % event)

    def remove_listener(self, event, listener):
        if valid_event(event):
            self._listeners[event].remove(listener)
        else:
            raise TypeError('Invalid IRC event %s.' % event)

    def run(self):
        loop = asyncio.get_event_loop()
        try:
            loop.run_until_complete(self._run())
        except KeyboardInterrupt:
            loop.run_until_complete(self._close())

        loop.close()

    # IRC messages
    async def privmsg(self, target, message):
        await self._send_raw("PRIVMSG {target} :{message}".format(target=target, message=message))

    # Internals
    def __repr__(self):
        return 'Client(host=%s, port=%d, user=%s)' % (self._host, self._port, self._user)

    async def _connect(self):
        if len(self._listeners['PING']) == 0:
            self.register_listener('PING', self._pong)

        self.register_listener('SERVER_NOTICE', self._auth_login)
        self.register_listener('BLANK_NOTICE', self._auth_login)

        self._reader, self._writer = await asyncio.open_connection(self._host, self._port)

    async def _read_line(self):
        line = await self._reader.readline()
        message = self._decode(line)
        return message

    def _decode(self, line):
        for decoder in self._decoders:
            try:
                (message, decoded_len) = decoder(line)
            except ValueError:
                pass

            if len(line) != decoded_len:
                logger.warning('Not all bytes decoded: %r' % line)

            return message.strip()

        raise RuntimeError("Failed to decode message")

    async def _close(self):
        if hasattr(self, '_reader'):
            await self._send_raw('QUIT :Exiting')
            self._writer.close()
            await self._writer.wait_closed()

    async def _send_raw(self, string):
        logger.debug("Sending line %s" % string)
        self._writer.write(str.encode('%s\r\n' % string))
        await self._writer.drain()

    # Event loop
    async def _run(self):
        await self._connect()
        tasks = set()
        reader = asyncio.create_task(self._read_line())
        tasks.add(reader)
        while True:
            done, tasks = await asyncio.wait(tasks, return_when=asyncio.FIRST_COMPLETED)
            for task in done:
                exception = task.exception()
                if exception is not None:
                    if task is reader:
                        raise exception
                    else:
                        logger.error("Error in event listener", exc_info=exception)

                if task is reader:
                    line = reader.result()
                    reader = asyncio.create_task(self._read_line())
                    tasks.add(reader)
                    event, parameters = parse(line)
                    if event is None:
                        logger.warning("Could not parse %r" % line)
                    else:
                        logger.debug("Got event %s with parameters %r" % (event, parameters))
                        for listener in self._listeners[event]:
                            tasks.add(listener(**parameters))
                        logger.debug("Called %d listeners" % len(self._listeners[event]))

    # Default event handlers
    async def _pong(self, timestamp):
        await self._send_raw('PONG %s' % timestamp)

    async def _auth_login(self, target, **kwargs):
        if target == 'AUTH':
            await self._send_raw('NICK %s' % self._nick)
            await self._send_raw('USER %s 0 * :%s' % (self._user, self._name))
            self.remove_listener('SERVER_NOTICE', self._auth_login)
            self.remove_listener('BLANK_NOTICE', self._auth_login)
