# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import time

from pyranha import async_ui_message
from pyranha.engine.listener import Listener
from pyranha.logging import log

class Channel(Listener):
    def __init__(self, network, name):
        self.network = network
        self.name = name
        self.nicks = []
        self.messages = []

    def add_message(self, source, message):
        self.messages.append((time.time(), source, message))
        async_ui_message('message', self.network, self)
