import re

from datetime import datetime

from .plugin import Plugin


class OldUrlPlugin(Plugin):
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_url)
        self._client = client
        self._regex = re.compile("http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\(\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+",
                                 re.IGNORECASE)

        super(OldUrlPlugin, self).__init__(config)

        if not self._store:
            self._store = {'url': {}, 'score': {}}

    def _handle_url(self, nick, target, message, **rest):
        if not target.startswith("#"):
            return

        urls = self._regex.findall(message)

        for url in urls:
            self.send_command(nick=nick, chan=target, url=url)

    def _handle_command(self, command):
        chan = command['chan']
        url = command['url']
        nick = command['nick']
        url_db = self._store['url']
        score_db = self._store['score']

        if chan not in url_db:
            url_db[chan] = {}

        if url not in url_db[chan]:
            url_db[chan][url] = [(nick, datetime.now())]
            self._logger.debug("Added url {url}", url=url)
            if nick in score_db:
                score_db[nick] += 1
            else:
                score_db[nick] = 1

        elif nick != url_db[chan][url][0][0]:
            url_db[chan][url].append((nick, datetime.now()))
            times = len(url_db[chan][url])
            if nick in score_db:
                score_db[nick] -= times
            else:
                score_db[nick] = -times

            self._client.privmsg(target=chan, message=self._config['format'].format(url=url, nick=nick,
                                                                                    times=times, score=score_db[nick]))
