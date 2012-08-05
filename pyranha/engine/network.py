# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from pyranha.engine.listener import Listener
from pyranha.engine.channel import Channel

class Network(Listener):
    def __init__(self, name, config, irc):
        self.irc = irc

        self.name = name
        self.nick = config['nick']
        self.server = config['servers'].keys()[0]
        self.password = config['servers'][self.server]['password']
        self.port = config['servers'][self.server]['port']
        self.ssl = config['servers'][self.server]['ssl']
        self.verify = config['servers'][self.server]['verify']

        self.connection = None
        self.channels = {}

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

        return self.connection

    def disconnect(self):
        if self.connection is not None:
            self.connection.disconnect()

    def raw(self, message):
        self.connection.send_raw(message)
