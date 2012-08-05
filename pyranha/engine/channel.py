# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from pyranha.engine.listener import Listener

class Channel(Listener):
    def test(self, **params):
        print 'listener test method, given params: ', params
