# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import Queue
import threading
import time

class UserInterface(threading.Thread):
    """Base class interface for separating UI into a separate thread using asynchronous messaging."""

    def __init__(self):
        super(UserInterface, self).__init__()
        self.messages = Queue.Queue()
        self.running = True

    def async_message(self, message_type, network=None, content=None):
        """Send an asynchronous message to the UI thread, with a given message
        type, network, and content.  This is generally to be called by other
        threads, but can also be called by the UI if it needs to reprocess a
        message later."""
        self.messages.put((message_type, network, content))

    def next_message(self, block=False):
        """Get the next message from the queue, returning a three-tuple with
        the message type, network, and the message content.  If the queue is
        empty, None will be returned for all values."""
        try:
            message_type, network, content = self.messages.get(block=block)
            return message_type, network, content

        except Queue.Empty:
            return None, None, None

    def run(self):
        while self.running:
            time.sleep(0.1)

    def stop(self):
        self.running = False
