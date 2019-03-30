import re


class ConverterPlugin():
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_conversion)
        self._client = client
        self._config = config
        self._pattern = re.compile('[0-9]+')

    async def _handle_conversion(self, message, nick, target, **rest):
        if message.startswith(self._config['trigger']):
            if target.startswith("#"):
                message = "{nick}: {response}".format(response=self._get_response(message), nick=nick)
                await self._client.privmsg(target=target, message=message)
            else:
                await self._client.privmsg(target=nick, message=self._get_response(message))

    def _get_response(self, message):
        matches = self._pattern.findall(message)

        return ' '.join(["{:08b}".format(int(match)) for match in matches])
