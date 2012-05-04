from __future__ import absolute_import, division

import sys
import select
import threading
import time

from pyranha.dotfiles import Dotfile
from pyranha.irc.client import IRC

class Engine(threading.Thread):

    def __init__(self):
        super(Engine, self).__init__()
        self.running = True
        self.input_buffer = ''

    def run(self):
        self.irc = IRC()
        self.irc.add_global_handler(event='all_events', handler=self._dispatch, priority=-1)
        self.network_config = Dotfile('networks', use_defaults=False)
        self.connections = {}
        self.networks = {}

        print 'starting engine...'

        for network in self.network_config:
            n = self.network_config[network]

            if n['connect']:
                address = n['servers'].keys()[0]
                port = n['servers'][address]['port']
                ssl = n['servers'][address]['ssl']
                password = n['servers'][address]['password']
                nick = n['nick']

                s = self.irc.server()
                self.networks[network] = s
                self.connections[s] = network

                print 'connecting to {}...'.format(network)
                s.connect(address, port, nick, password=password, username='pyranha', ircname='pyranha user', ssl=ssl)

        self.process_forever()
        self.stop()

    def stop(self):
        for network in self.networks:
            s = self.networks[network]
            print 'disconnecting from {}...'.format(network)
            s.disconnect()

        for i in range(100):
            self.irc.process_once()
            time.sleep(0.02)

        print 'bye'

    def process_forever(self):
        while self.running:
            #print 'irc.process_forever()'
            self.irc.process_once()

            #print 'select.select()'
            rready, wready, xready = select.select([sys.stdin,], [], [], 0.0)
            if rready:
                command = sys.stdin.readline().strip()

                print 'raw command: "{}"'.format(command)
                if command == 'quit':
                    print 'stopping'
                    self.running = False
                    continue

                for s in self.connections:
                    s.send_raw(command)

    def _dispatch(self, conn, event):
        print conn.server, event.eventtype(), event.source(), event.target(), event.arguments()


