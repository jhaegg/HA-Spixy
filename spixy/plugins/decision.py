from random import choice

from .plugin import Plugin


class DecisionPlugin(Plugin):
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_decision)
        self._client = client
        super(DecisionPlugin, self).__init__(config)

    def _handle_decision(self, nick, target, message, **rest):
        if message.startswith('%d'):
            self.send_command(nick=nick, target=target)

    def _handle_command(self, command):
        if command['target'].startswith("#"):
            self._client.privmsg(target=command['target'],
                                 message="{nick}: {answer}".format(answer=choice(self._config['choices']), **command))
        else:
            self._client.privmsg(target=command['nick'], message=choice(self._config['choices']))
