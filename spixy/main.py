from importlib import import_module
from json import load

from spixy.irc.client import Client


def main():
    with open('config/spixy.json') as f:
        config = load(f)

    client = Client(**config['server'])
    load_plugins(config['plugins'], client)
    client.run()


def load_plugins(plugins, client):
    for plugin in plugins:
        module_path, initializer = plugin['module'].split(':')
        module = import_module(module_path)
        getattr(module, initializer)(plugin['config'], client)

if __name__ == '__main__':
    main()
