# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from pyranha.logging import log

class Listener(object):

    def notify(self, event_type, *args, **params):
        try:
            method = getattr(self, 'on_' + event_type)
        except AttributeError:
            log.warning('{0} does not support {1}'.format(self, event_type))
        else:
            method(*args, **params)
