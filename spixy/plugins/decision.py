from random import choice

from .plugin import Plugin


class DecisionPlugin(Plugin):
    def __init__(self, client):
        client.register_listener("PRIVMSG", self._handle_decision)
        self._client = client
        super(DecisionPlugin, self).__init__()

    def _handle_decision(self, nick, target, message, **rest):
        if message.startswith('%d'):
            self.send_command(nick=nick, target=target)

    def _handle_command(self, command):
        if command['target'].startswith("#"):
            self._client._send_raw('PRIVMSG {target} :{nick}: {answer}'.format(answer=choice(['Yes', 'No']), **command))
        else:
            self._client._send_raw('PRIVMSG {nick} :{answer}'.format(answer=choice(['Yes', 'No']), **command))
