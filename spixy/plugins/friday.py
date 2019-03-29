from datetime import date


class FridayPlugin():
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_friday)
        self._client = client
        self._config = config

    async def _handle_friday(self, message, nick, target, **rest):
        if message.startswith(self._config['trigger']):
            if target.startswith("#"):
                message = "{nick}: {response}".format(response=self._get_response(), target=target)
                await self._client.privmsg(target=target, message=message)
            else:
                await self._client.privmsg(target=nick, message=self._get_response())

    def _get_response(self):
        today = date.today().strftime('%A')
        if today == 'Friday':
            return "Yes, it's {today}!".format(today=today)
        else:
            return "No, it's {today}.".format(today=today)
