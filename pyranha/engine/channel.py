# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from pyranha.engine.listener import Listener
from pyranha.logging import log

class Channel(Listener):
    def test(self, **params):
        log.info('listener test method, given params: {0}'.format(params))
