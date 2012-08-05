# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import Queue
import sys
import select
import threading
import time

from pyranha import async_ui_message
from pyranha.dotfiles import Dotfile
from pyranha.irc.client import IRC
from pyranha.engine.network import Network

class Engine(threading.Thread):

    def __init__(self):
        super(Engine, self).__init__()
        self.running = True
        self.commands = Queue.Queue()

    def async_command(self, command, network=None, params=None):
        """Send an asynchronous command to engine thread, for the given network
        with the given parameters.  This is generally meant to be called from
        the UI thread, but can also be used to queue a command from the engine.
        A network value of '*' will send the command to all networks that are
        currently connected."""
        self.commands.put((command, network, params))

    def next_command(self, block=False, timeout=None):
        """Get the next command from the queue, return a three-tuple with the
        command, network, and parameters.  If the queue is empty and block is
        false, None will be returned for all values."""
        try:
            command, network, params = self.commands.get(block=block)
            return command, network, params

        except Queue.Empty:
            return None, None, None

    def run(self):
        self.irc = IRC()
        self.irc.add_global_handler(event='all_events', handler=self.process_events, priority=-1)
        self.network_config = Dotfile('networks', use_defaults=False)
        self.connections = {}
        self.networks = {}

        async_ui_message('debug', None, 'starting engine')

        irc_thread = threading.Thread(target=self.process_irc)
        irc_thread.start()

        command_thread = threading.Thread(target=self.process_commands)
        command_thread.start()

        while command_thread.is_alive():
            command_thread.join()
        async_ui_message('debug', None, 'command_thread stopped')

        while irc_thread.is_alive():
            irc_thread.join()
        async_ui_message('debug', None, 'irc_thread stopped')

        async_ui_message('print', None, 'bye')
        async_ui_message('stopped')

    def process_irc(self):
        while self.running:
            try:
                self.irc.process_once(timeout=1)
            except Exception as e:
                async_ui_message('debug', None, 'exception in process_irc: {0}'.format(e))

    def process_commands(self):
        while self.running:
            try:
                command, network, params = self.next_command(block=True)
                async_ui_message('debug', network, 'processing command {0} with parameters {1}'.format(command, params))

                method = 'command_' + command
                if hasattr(self, method):
                    getattr(self, method)(network, params)
                else:
                    async_ui_message('debug', network, 'method {0} not found, command discarded'.format(method))

            except Exception as e:
                async_ui_message('debug', None, 'exception processing command: {0}'.format(e))

    def process_events(self, conn, event):
        try:
            network = self.connections[conn]

            method = 'on_' + event.eventtype()
            getattr(network, method)(event)

        except Exception as e:
            async_ui_message('debug', None, 'exception during dispatch: {0}'.format(e))

    def command_connect(self, name, params, explicit=True):
        if name is None:
            for name in self.network_config:
                self.command_connect(name, params, explicit=False)

        elif name in self.network_config:
            if explicit or self.network_config[name]['connect']:
                network = Network(name, self.network_config[name], self.irc)
                connection = network.connect()

                self.networks[name] = network
                self.connections[connection] = network

        else:
            async_ui_message('print', name, 'network {0} not found in configuration, could not connect'.format(name))

    def command_raw(self, network, params):
        if network == '*':
            async_ui_message('print', '*', 'sending raw command to all networks: {0}'.format(params))
            for network in self.networks.values():
                network.raw(params)
        else:
            network = self.networks[network]
            async_ui_message('print', network.name, 'sending raw command: {0}'.format(params))
            network.raw(params)

    def command_stop(self, network, params):
        for network in self.networks.values():
            async_ui_message('print', network.name, 'disconnecting...')
            network.disconnect()
        time.sleep(1)
        self.running = False

