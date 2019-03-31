import asyncio

from aiosqlite import Connection
from sqlite3 import connect


class SQLitePool():
    def __init__(self, path):
        self._path = path

    def acquire(self):
        def connector():
            return connect(self._path)

        return Connection(connector, asyncio.get_event_loop())
