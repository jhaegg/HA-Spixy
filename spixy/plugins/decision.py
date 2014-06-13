from random import choice

from .plugin import Plugin


class DecisionPlugin(Plugin):
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_decision)
        self._client = client
        super(DecisionPlugin, self).__init__(config)

    def _handle_decision(self, nick, target, message, **rest):
        if message.startswith(self._config['trigger'] + " "):
            self.send_command(nick=nick, target=target, message=message)

    def _handle_command(self, command):
        choices = self._partition(command['message'])

        if len(choices) == 1:
            answer = choice(self._config['choices'])
        else:
            answer = choice(choices)

        if command['target'].startswith("#"):
            self._client.privmsg(target=command['target'],
                                 message="{nick}: {answer}".format(answer=answer, **command))
        else:
            self._client.privmsg(target=command['nick'], message=answer)

    def _partition(self, message):
        parts = [message[len(self._config['trigger']):]]
        for separator in self._config['separators']:
            new_parts = set()
            for part in parts:
                [new_parts.add(s.strip()) for s in part.split(separator)]

            parts = new_parts

        return list(parts)
