import re

from .plugin import Plugin


class ConverterPlugin(Plugin):
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_conversion)
        self._client = client
        self._pattern = re.compile('[0-9]+')
        super(ConverterPlugin, self).__init__(config)

    def _handle_conversion(self, message, nick, target, **rest):
        if message.startswith(self._config['trigger']):
            self.send_command(nick=nick, target=target, message=message)

    def _handle_command(self, command):
        if command['target'].startswith("#"):
            self._client.privmsg(target=command['target'],
                                 message="{nick}: {response}".format(response=self._get_response(command['message']), **command))
        else:
            self._client.privmsg(target=command['nick'], message=self._get_response(command['message']))

    def _get_response(self, message):
        matches = self._pattern.findall(message)

        return ' '.join(["{:08b}".format(int(match)) for match in matches])
