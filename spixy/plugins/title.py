from .plugin import Plugin

from re import compile, IGNORECASE
from html import unescape

from requests_futures.sessions import FuturesSession
from requests.exceptions import RequestException


class TitlePlugin(Plugin):
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_title)
        self._client = client
        self._pages = {}
        self._titles_fetched = False
        self._url_match = compile('https?://[^\s/$.?#].[^\s]*')
        self._title_match = compile('<title>(.+?)</title>', IGNORECASE)
        self._session = FuturesSession(max_workers=5)

        super(TitlePlugin, self).__init__(config)

    def _handle_title(self, nick, target, message, **rest):
        pages = self._url_match.findall(message)
        if pages:
            self._pages = {page: None for page in pages}
            self._titles_fetched = False

        if message.startswith(self._config['trigger']):
            if self._pages:
                self.send_command(nick=nick, target=target)

    def _handle_command(self, command):
        if command['target'].startswith("#"):
            prefix = "{nick}: ".format(**command)
            target = command['target']
        else:
            prefix = ""
            target = command['nick']

        multiple = len(self._pages) > 1

        if not self._titles_fetched:
            self._async_send_titles(prefix, target, self._pages.keys(), multiple)
            self._titles_fetched = True
        else:
            for page, title in self._pages.items():
                self._send_title(prefix, target, page, title, multiple)

    def _async_send_titles(self, prefix, target, pages, multiple):
        #futures = [self._session.get(page, background_callback=self._title_callback(prefix, target, page, multiple), stream=True)
        futures = [self._session.get(page, background_callback=self.callback, stream=True)
                   for page in pages]

        # Must "join" requests-futures requests for some odd reason.
        for future in futures:
            future.result()

    #def _title_callback(self, prefix, target, page, multiple):
    def callback(session, response):
        try:
            if int(response.headers['content-length']) < 5000000:
                response.raise_for_status()
            else:
                response.close()
                self._pages[page] = "Error, no title found."
                return callback
        except RequestException:
            self._logger.exception("Got status {status} when retrieving {page}".format(status=response.status_code,
                                                                                       page=page))
            self._pages[page] = "Error, status code {status}".format(status=response.status_code)
            self._send_title(prefix, target, page, self._pages[page], multiple)
            return

        try:
            title = self._title_match.search(response.text).group(1)
            self._pages[page] = unescape(title)
            self._send_title(prefix, target, page, title, multiple)
            return
        except AttributeError:
            self._pages[page] = "Error, no title found."
            self._send_title(prefix, target, page, self._pages[page], multiple)

    return callback

    def _send_title(self, prefix, target, page, title, multiple):
        if title is None:
            return

        if multiple:
            message = "{prefix}{page} - {title}".format(prefix=prefix, page=page, title=title)
        else:
            message = "{prefix}{title}".format(prefix=prefix, title=title)

        self._client.privmsg(target, message)
