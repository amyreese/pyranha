# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from pyranha.logging import log
import pyranha.irc.client

class Listener(object):

    def notify(self, *args, **params):
        try:
            event = args[0]

            t = type(event)
            if t == str:
                event_type = event
                args.pop(0)
            elif t == pyranha.irc.client.Event:
                event_type = event.eventtype()

            event_type = event_type.replace('-', '_')
            method = getattr(self, 'on_' + event_type)

        except AttributeError:
            log.warning('{0} does not support {1}'.format(self, event_type))
        else:
            method(*args, **params)
