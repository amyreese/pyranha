# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import random

from pyranha import async_ui_message, async_engine_command
from pyranha.engine.listener import Listener
from pyranha.engine.channel import Channel
from pyranha.logging import log, log_irc_event

class Network(Listener):
    def __init__(self, name, config, irc):
        self.irc = irc

        self.name = name
        self.config = config
        self.nick = config['nick']
        self.server = config['servers'].keys()[0]
        self.password = config['servers'][self.server]['password']
        self.port = config['servers'][self.server]['port']
        self.ssl = config['servers'][self.server]['ssl']
        self.verify = config['servers'][self.server]['verify']

        self.connected = False
        self.connection = None
        self.root = Channel(self, '')
        self.channels = {}

        async_ui_message('new_channel', self, self.root)

    def __repr__(self):
        return '<pyranha.Network({0})>'.format(self.name)

    def __str__(self):
        return 'Network({0})'.format(self.name)

    def connect(self):
        self.connection = self.irc.server()
        self.connection.connect(self.server,
                                self.port,
                                self.nick,
                                password=self.password,
                                username='pyranha',
                                ircname='pyranha',
                                ssl=self.ssl,
                                )

        self.connected = False
        self.nick_retry = 0

        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.disconnect()
        self.connected = False

    def raw(self, message):
        self.connection.send_raw(message)

    def on_join(self, event):
        name = event.target()
        channel = Channel(self, name)
        self.channels[name] = channel

        async_ui_message('new_channel', self, channel)

    def on_ping(self, event):
        self.root.add_message(event.source(), 'PING!')
        self.connection.pong(*event.arguments())
        self.root.add_message(event.source(), 'PONG!')

    def on_pubmsg(self, event):
        name = event.target()
        if name not in self.channels:
            channel = Channel(self, name)
            self.channels[name] = channel
        else:
            channel = self.channels[name]
        channel.add_message(event.source(), event.arguments()[0])

    def on_nicknameinuse(self, event):
        if not self.connected:
            if self.nick_retry < 2:
                self.nick += ''
            else:
                self.nick = 'pyranha' + str(random.randint(1000, 9999))

            self.nick_retry += 1
            self.connection.nick(self.nick)

        else:
            self.root.add_message(event.source(), event.arguments()[1])

    def on_welcome(self, event):
        log_irc_event(event)
        self.connected = True
        self.nick = event.target()
        self.root.add_message(event.source(), event.arguments()[0])

        for channel in self.config['channels']:
            key = self.config['channels'][channel]
            key = '' if key is None else key

            if not channel.startswith('#'):
                channel = '#' + channel

            log.info('auto-joining {0}'.format(channel))
            self.connection.join(channel, key=key)
