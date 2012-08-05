# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

class Listener(object):

    def notify(self, event_type, **params):
        try:
            m = getattr(self, event_type)
            m(**params)
        except:
            print self, ' does not have event listener method ', event_type
