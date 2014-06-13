from .plugin import Plugin
from datetime import date


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
                                 message="{nick}: {response}".format(response=self._get_response(), **command))
        else:
            self._client.privmsg(target=command['nick'], message=self._get_response())

    def _get_response(self):
        today = date.today().strftime('%A')
        if today == 'Friday':
            return "Yes, it's {today}!".format(today=today)
        else:
            return "No, it's {today}.".format(today=today)