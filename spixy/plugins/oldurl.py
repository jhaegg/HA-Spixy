import asyncio
import re

from time import time, mktime

from sqlite3 import OperationalError
from pickle import load
from pypika import Table


class OldUrlPlugin():
    def __init__(self, config, client, db, builder):
        client.register_listener("PRIVMSG", self._handle_url)
        self._client = client
        self._db = db
        self._builder = builder
        self._db_initialized = False
        self._regex = re.compile(r"https?://[^\s/$.?#].[^\s]*", re.IGNORECASE)

    async def _handle_url(self, nick, target, message, **rest):
        await self._init_db()
        if not target.startswith("#"):
            return

        urls = self._regex.findall(message)

        pending = set()
        for url in urls:
            pending.add(self._check_old(nick, target, url))

        await asyncio.gather(*pending)

    async def _check_old(self, nick, chan, url):
        times, by = await self._get_times_posted(chan, url)

        if by != nick:
            if times > 0:
                await self._increment_times(chan, url)
                times += 1
                await self._modify_score(nick, -times)
                score = await self._get_score(nick)
                if score is None:
                    score = await self._new_score(nick, -times)

                response = self._config['format'].format(
                    by=by, nick=nick, url=url, times=times, score=score)

                await self._client.privmsg(message=response, target=chan)
            else:
                await self._new_url(chan, url, nick, int(time()))
                await self._modify_score(nick, 1)

    async def _get_times_posted(self, chan, url):
        table = Table("url")
        stmt = self._builder.from_(table).select("times", "nick").\
            where((table.chan == chan) & (table.url == url))

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt.get_sql())
                result = await cursor.fetchone()
                if result is None:
                    return 0, ""

                return result

    async def _increment_times(self, chan, url):
        table = Table("url")
        stmt = self._builder.update(table).set(table.times, table.times + 1).\
            where((table.chan == chan) & (table.url == url))

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt.get_sql())

            await conn.commit()

    async def _modify_score(self, nick, score_modifier):
        table = Table("score")
        stmt = self._builder.update(table).\
            set(table.score, table.score + score_modifier).\
            where(table.nick == nick)

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt.get_sql())

            await conn.commit()

    async def _get_score(self, nick):
        table = Table("score")
        stmt = self._builder.from_(table).select("score").\
            where(table.nick == nick)

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt.get_sql())
                result = await cursor.fetchone()
                if result is None:
                    return None

                return result[0]

    async def _new_score(self, nick, starting_score):
        table = Table("score")
        stmt = self._builder.into(table).columns("nick", "score").\
            insert(nick, starting_score)

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt.get_sql())

            await conn.commit()

        return starting_score

    async def _new_url(self, chan, url, nick, timestamp):
        table = Table("url")
        stmt = self._builder.into(table).\
            columns("chan", "url", "nick", "times", "timestamp").\
            insert(chan, url, nick, 1, timestamp)

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                await cursor.execute(stmt.get_sql())

            await conn.commit()

    async def _init_db(self):
        if self._db_initialized:
            return

        async with self._db.acquire() as conn:
            async with conn.cursor() as cursor:
                try:
                    await cursor.execute("""
                        CREATE TABLE url (
                            chan      TEXT    NOT NULL,
                            url       TEXT    NOT NULL,
                            nick      TEXT    NOT NULL,
                            times     INTEGER NOT NULL,
                            timestamp INTEGER NOT NULL,

                            CONSTRAINT idx_chan_url PRIMARY KEY (chan, url)
                        );""")

                    await cursor.execute("""
                        CREATE TABLE score (
                            nick  TEXT PRIMARY KEY,
                            score INTEGER NOT NULL
                        );""")

                    # Untested
                    with open("config/OldUrlPlugin.pickle") as pickle:
                        store = load(pickle)

                    url_table = Table("url")
                    stmt = self._builder.into(url_table).\
                        columns("chan", "url", "nick", "times", "timestamp")

                    for chan, urls in store['url'].items():
                        for url, info in urls.items():
                            nick, when = info
                            timestamp = mktime(when.timetuple())
                            stmt = stmt.insert(chan, url, nick, 1, timestamp)

                    await cursor.execute(stmt.get_sql())

                    score_table = Table("score")
                    stmt = self._builder.into(score_table).\
                        columns("nick", "score")

                    for nick, score in store['score'].items():
                        stmt = stmt.insert(nick, score)

                    await cursor.execute(stmt.get_sql())

                except OperationalError:
                    pass
                except FileNotFoundError:
                    pass

            await conn.commit()
            self._db_initialized = True
