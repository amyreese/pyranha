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
from pyranha.logging import log

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

        log.info('starting engine')

        irc_thread = threading.Thread(target=self.process_irc)
        irc_thread.start()

        command_thread = threading.Thread(target=self.process_commands)
        command_thread.start()

        while command_thread.is_alive():
            command_thread.join()
        log.debug('command_thread stopped')

        while irc_thread.is_alive():
            irc_thread.join()
        log.debug('irc_thread stopped')

        async_ui_message('stopped')

    def process_irc(self):
        while self.running:
            try:
                self.irc.process_once(timeout=1)
            except Exception as e:
                log.exception('exception in process_irc: {0}'.format(e))

    def process_commands(self):
        while self.running:
            try:
                command, network, params = self.next_command(block=True)
                log.info('processing command {0} from {1} with parameters {2}'.format(command, network, params))

                method = 'command_' + command
                if hasattr(self, method):
                    getattr(self, method)(network, params)
                else:
                    log.warning('method {0} not found, command discarded'.format(method))

            except Exception as e:
                log.exception('exception processing command: {0}'.format(e))

    def process_events(self, conn, event):
        try:
            network = self.connections[conn]

            if event.eventtype() != 'all_raw_messages':
                network.notify(event)

        except Exception as e:
            log.exception('exception during dispatch: {0}'.format(e))

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
            log.warning('network {0} not found in configuration, could not connect'.format(name))

    def command_send(self, network, (channel, message)):
        log.debug('send message to {0} {1}: {2}'.format(network, channel, message))
        self.command_raw(network.name, message)

    def command_raw(self, network, params):
        if network == '*':
            log.info('sending raw command to all networks: {0}'.format(params))
            for network in self.networks.values():
                network.raw(params)
        else:
            network = self.networks[network]
            log.info('sending raw command to {0}: {1}'.format(network.name, params))
            network.raw(params)

    def command_stop(self, network, params):
        for network in self.networks.values():
            log.info('disconnecting {0}...'.format(network.name))
            network.disconnect()
        time.sleep(1)
        self.running = False

