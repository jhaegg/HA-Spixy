class AutoJoinPlugin():
    def __init__(self, config, client):
        client.register_listener("REPLY", self._handle_connect)
        self._client = client
        self._config = config

    async def _handle_connect(self, code, **rest):
        if code == "001":
            self._client.remove_listener("REPLY", self._handle_connect)
            for channel in self._config['channels']:
                await self._client._send_raw("JOIN %s" % channel)
