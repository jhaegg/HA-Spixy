from json import load
from threading import Thread

from spixy.irc.client import Client
from spixy.plugins.decision import DecisionPlugin

class RawSender(Thread):
    def __init__(self, client):
        Thread.__init__(self)
        self.client = client

    def run(self):
        command = ''
        while command != '/quit':
            command = input('>:')
            if command != '/quit':
                client._send_raw(command)

def join_on_connect(config):
    def wrapped(host, code, target, message):
        if code == '001':
            for channel in config['autojoin']:
                client._send_raw("JOIN %s" % channel)

    return wrapped

if __name__ == '__main__':
    with open('config/spixy.json') as f:
        config = load(f)

    client = Client(**config['server'])
    client.register_listener('REPLY', join_on_connect(config))
    console = RawSender(client)
    client.connect()
    decision = DecisionPlugin(config, client)
    console.start()
    console.join()
    decision.close()
    client.close()
