from __future__ import absolute_import, division

import Queue
import sys
import select
import threading
import time

from pyranha import async_ui_message
from pyranha.dotfiles import Dotfile
from pyranha.irc.client import IRC

class Engine(threading.Thread):

    def __init__(self):
        super(Engine, self).__init__()
        self.running = True
        self.commands = Queue.Queue()

    def async_command(self, network, command, params=None):
        """Send an asynchronous command to engine thread, for the given network
        with the given parameters.  This is generally meant to be called from
        the UI thread, but can also be used to queue a command from the engine.
        A network value of '*' will send the command to all networks that are
        currently connected."""
        self.commands.put((network, command, params))

    def next_command(self, block=False, timeout=None):
        """Get the next command from the queue, return a three-tuple with the
        network, command, and parameters.  If the queue is empty and block is
        false, None will be returned for all values."""
        try:
            network, command, params = self.commands.get(block=block)
            return network, command, params

        except Queue.Empty:
            return None, None, None

    def run(self):
        self.irc = IRC()
        self.irc.add_global_handler(event='all_events', handler=self._dispatch, priority=-1)
        self.network_config = Dotfile('networks', use_defaults=False)
        self.connections = {}
        self.networks = {}

        async_ui_message(None, 'debug', 'starting engine')

        irc_thread = threading.Thread(target=self.process_irc)
        irc_thread.start()

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

                async_ui_message(network, 'print', 'connecting...')
                s.connect(address, port, nick, password=password, username='pyranha', ircname='pyranha user', ssl=ssl)

        command_thread = threading.Thread(target=self.process_commands)
        command_thread.start()

        while command_thread.is_alive():
            command_thread.join()
        async_ui_message(None, 'debug', 'command_thread stopped')

        while irc_thread.is_alive():
            irc_thread.join()
        async_ui_message(None, 'debug', 'irc_thread stopped')

        async_ui_message(None, 'print', 'bye')
        async_ui_message(None, 'stopped')

    def process_commands(self):
        while self.running:
            try:
                network, command, params = self.next_command(block=True)
                if network in self.networks:
                    s = self.networks[network]
                    async_ui_message(network, 'debug', 'sending raw command: ' + command)
                    s.send_raw(command)
                elif network == '*':
                    for s in self.connections:
                        async_ui_message(network, 'debug', 'sending raw command: ' + command)
                        s.send_raw(command)
                elif command == 'stop':
                    for network in self.networks:
                        s = self.networks[network]
                        async_ui_message(network, 'print', 'disconnecting...')
                        s.disconnect()
                    time.sleep(1)
                    self.running = False

            except Exception as e:
                async_ui_message(None, 'debug', 'exception occurred: {0}'.format(e))

    def process_irc(self):
        while self.running:
            try:
                self.irc.process_once(timeout=1)
            except Exception as e:
                async_ui_message(None, 'debug', 'exception in process_irc: {0}'.format(e))

    def stop(self):
        self.running = False

    def _dispatch(self, conn, event):
        try:
            network = None
            if conn in self.connections:
                network = self.connections[conn]

            t = event.eventtype()
            if t == 'ping':
                async_ui_message(network, 'print', 'PING PONG')
                self.async_command(network, ' '.join(['PONG'] + event.arguments()))

            elif t == 'all_raw_messages':
                pass
            else:
                async_ui_message(network, 'print', 'type: {0}, source: {1}, target: {2}, arguments: {3}'.format(t, event.source(), event.target(), event.arguments()))

        except Exception as e:
            async_ui_message(None, 'debug', 'exception during dispatch: {0}'.format(e))
