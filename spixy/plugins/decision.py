from random import choice

from .util import chan_or_user


class DecisionPlugin():
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_decision)
        self._client = client
        self._config = config

    async def _handle_decision(self, message, nick, target, **rest):
        if message.startswith(self._config['trigger'] + " "):
            choices = self._partition(message)
            if len(choices) == 1:
                response = choice(self._config['choices'])
            else:
                response = choice(choices)

            await self._client.privmsg(**chan_or_user(response, nick, target))

    def _partition(self, message):
        if self._config['indicator'] not in message:
            return [message]

        parts = [message[len(self._config['trigger']):]]
        for separator in self._config['separators']:
            new_parts = set()
            for part in parts:
                [new_parts.add(s.strip().strip('?')) for s in part.split(separator)]

            parts = new_parts

        return list(parts)
