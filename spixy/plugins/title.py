import asyncio
from html import unescape
from re import compile, IGNORECASE, MULTILINE, UNICODE

from aiohttp import request

from .util import chan_or_user


class TitlePlugin():
    def __init__(self, config, client):
        client.register_listener("PRIVMSG", self._handle_title)
        self._client = client
        self._config = config
        self._titles = []
        self._url_match = compile(r'https?://[^\s/$.?#].[^\s]*')
        self._title_match = compile(r'<title>(.+)<\/title>', IGNORECASE | MULTILINE | UNICODE)

    async def _handle_title(self, message, nick, target, **rest):
        pages = self._url_match.findall(message)
        if pages:
            self._titles = await asyncio.gather(*(self._load_page(page) for page in pages))

        if message.startswith(self._config['trigger']):
            if len(self._titles) > 1:
                fmt = "{page} - {title}"
            else:
                fmt = "{title}"

            for page, title in self._titles:
                response = fmt.format(page=page, title=title)
                await self._client.privmsg(**chan_or_user(response, nick, target))

    async def _load_page(self, page):
        headers = self._config['headers']
        try:
            async with request('HEAD', page, headers=headers) as head_response:
                head_response.raise_for_status()
                if "text" not in head_response.headers['Content-Type']:
                    return page, "Error, no title found."

            async with request('GET', page, headers=headers) as response:
                response.raise_for_status()
                text = await response.text()

            title = self._title_match.search(text).group(1)
            return page, unescape(title)
        except Exception:
            return page, "Error, no title found."
