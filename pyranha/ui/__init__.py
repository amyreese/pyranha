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

    def async_message(self, network, message_type, content=None):
        """Send an asynchronous message to the UI thread, with a given network, message type
        and content.  This is generally to be called by other threads, but can also be called
        by the UI if it needs to reprocess a message later."""
        self.messages.put((network, message_type, content))

    def next_message(self, block=False):
        """Get the next message from the queue, returning a three-tuple with the network,
        message type and the message content.  If the queue is empty, None will be returned
        for all values."""
        try:
            network, message_type, content = self.messages.get(block=block)
            return network, message_type, content

        except Queue.Empty:
            return None, None, None

    def run(self):
        while self.running:
            time.sleep(0.1)

    def stop(self):
        self.running = False
