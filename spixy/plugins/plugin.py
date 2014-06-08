from collections import deque
from threading import Thread
from time import sleep

_MagicQuit = 0x00ff00ff


class Plugin(Thread):
    def __init__(self, config):
        self._command_channel = deque()
        self._config = config[self.__class__.__name__]
        super(Plugin, self).__init__()
        self.start()

    def send_command(self, **command):
        self._command_channel.append(command)

    def run(self):
        while (True):
            try:
                command = self._command_channel.popleft()
                if command == _MagicQuit:
                    self._cleanup()
                    break

                self._handle_command(command)
            except IndexError:
                sleep(0.5)

    def _handle_command(self, command):
        raise NotImplemented

    def _cleanup(self):
        pass

    def close(self):
        self._command_channel.append(_MagicQuit)
        self.join()
