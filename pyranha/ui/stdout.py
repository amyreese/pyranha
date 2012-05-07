# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import select
import signal
import sys

from pyranha import async_engine_command
from pyranha.ui import UserInterface

class StdoutUI(UserInterface):

    def __init__(self):
        super(StdoutUI, self).__init__()

    def run(self):
        async_engine_command('connect')

        while self.running:
            while True:
                message_type, network, content = self.next_message()
                if message_type is None:
                    break

                if message_type == 'print' or message_type == 'debug':
                    print '{0}: {1}'.format(network, content)

                elif message_type == 'stopped':
                    print 'ui received engine stopped'
                    self.running = False

                else:
                    source, target, arguments = content
                    print '{0}: {1} from {2} to {3} with {4}'.format(network, message_type, source, target, arguments)

            r, w, x = select.select([sys.stdin,], [], [], 0.01)
            if r:
                command = sys.stdin.readline().strip()

                if command == '':
                    pass

                elif command == 'quit':
                    async_engine_command('stop')

                else:
                    async_engine_command('raw', '*', command)
