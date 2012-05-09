# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command
from pyranha.ui import UserInterface

class GtkUI(UserInterface):

    def __init__(self):
        GObject.threads_init()
        Gdk.threads_init()
        super(GtkUI, self).__init__()

    def async_message(self, message_type, network=None, content=None):
        """Override the default async_message implementation to tell Gtk's main loop
        to run process_message with the given message attributes."""
        print 'queueing idle_add: {0}, {1}, {2}'.format(message_type, network, content)
        GObject.idle_add(self.process_message, (message_type, network, content))

    def run(self):
        async_engine_command('connect')

        window = Gtk.Window()
        window.connect('delete-event', self.stop)
        window.show_all()
        Gtk.main()

    def stop(self, widget, event):
        async_engine_command('stop')

    def process_message(self, (message_type, network, content)):
        print 'in process_message: {0}, {1}, {2}'.format(message_type, network, content)
        if message_type == 'stopped':
            Gtk.main_quit()
