from .plugin import Plugin


class FridayPlugin(Plugin):
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_friday)
        self._client = client
        super(FridayPlugin, self).__init__(config)

    def _handle_friday(self, message, nick, target, **rest):
        if message.startswith(self._config['trigger']):
            self.send_command(nick=nick, target=target)

    def _handle_command(self, command):
        if command['target'].startswith("#"):
            self._client.privmsg(target=command['target'],
                                 message="{nick}: Yes, it's Friday!".format(**command))
        else:
            self._client.privmsg(target=command['nick'], message="Yes, it's Friday!")
