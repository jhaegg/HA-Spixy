from datetime import date

from .util import chan_or_user


class FridayPlugin():
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_friday)
        self._client = client
        self._config = config

    async def _handle_friday(self, message, nick, target, **rest):
        if message.startswith(self._config['trigger']):
            response = self._get_response()
            await self._client.privmsg(**chan_or_user(response, nick, target))

    def _get_response(self):
        today = date.today().strftime('%A')
        if today == 'Friday':
            return "Yes, it's {today}!".format(today=today)
        else:
            return "No, it's {today}.".format(today=today)
