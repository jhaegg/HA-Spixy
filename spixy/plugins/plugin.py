from collections import deque
import logging
from threading import Thread
from time import sleep
from pickle import load, dump, PicklingError, UnpicklingError

_MagicQuit = 0x00ff00ff
_levels = {
    'critical': logging.CRITICAL,
    'error': logging.ERROR,
    'warn': logging.WARN,
    'warning': logging.WARNING,
    'info': logging.INFO,
    'debug': logging.DEBUG
}


class Plugin(Thread):
    def __init__(self, config):
        self._command_channel = deque()
        self._config = config.get(self.__class__.__name__, {})
        self._logger = logging.getLogger(self.__class__.__name__)
        if 'loglevel' in self._config:
            try:
                self._logger.setLevel(self, _levels[self._config['loglevel']])
            except KeyError:
                self._logger.error("Unknown logging level %s" % self._config['loglevel'])

        super(Plugin, self).__init__()
        filename = "config/" + self.__class__.__name__ + ".pickle"
        try:
            with open(filename, 'rb') as f:
                self._store = load(f)
        except (IOError, EOFError):
            self._logger.exception("Could not open %s for reading, no persistent data loaded." % filename)
            self._store = {}
        except UnpicklingError:
            self._logger.exception("Error loading persistent data from %s." % filename)
            self._store = {}

        self.start()

    def send_command(self, **command):
        self._command_channel.append(command)

    def run(self):
        while True:
            try:
                command = self._command_channel.popleft()
                if command == _MagicQuit:
                    self._cleanup()
                    break

                try:
                    self._handle_command(command)
                except:
                    self._logger.exception("Uncaught exception handling command:\n%r" % command)

            except IndexError:
                sleep(0.5)

    def _handle_command(self, command):
        raise NotImplemented

    def _cleanup(self):
        filename = "config/" + self.__class__.__name__ + ".pickle"
        try:
            with open(filename, 'wb') as f:
                dump(self._store, f)
        except IOError:
            self._logger.exception("Could not open %s for writing, persistent data not saved." % filename)
        except PicklingError:
            self._logger.exception("Error saving persistent data from %s." % filename)

    def close(self):
        self._command_channel.append(_MagicQuit)
        self.join()
