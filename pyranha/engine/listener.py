# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

class Listener(object):

    def notify(self, event_type, *args, **params):
        try:
            getattr(self, 'on_' + event_type)(*args, **params)
        except:
            print self, ' does not have event listener method ', event_type
