from json import load

from spixy.irc.client import Client
from spixy.plugins.friday import FridayPlugin

def main():
    with open('config/spixy.json') as f:
        config = load(f)

    client = Client(**config['server'])
    FridayPlugin(config['FridayPlugin'], client)
    client.run()


if __name__ == '__main__':
    main()
