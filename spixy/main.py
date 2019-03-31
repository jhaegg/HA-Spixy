from importlib import import_module
from json import load

from pypika import SQLLiteQuery

from .db import SQLitePool
from spixy.irc.client import Client


def main():
    with open('config/spixy.json') as f:
        config = load(f)

    client = Client(**config['server'])
    load_plugins(config['plugins'], client)
    client.run()


def load_plugins(plugins, client):
    for plugin in plugins:
        module_path, initializer_name = plugin['module'].split(':')
        module = import_module(module_path)
        initializer = getattr(module, initializer_name)
        config = plugin['config']

        if 'db' in plugin:
            pool = SQLitePool(plugin['db'])
            builder = SQLLiteQuery
            initializer(config, client, pool, builder)
        else:
            initializer(config, client)


if __name__ == '__main__':
    main()
