# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command
from pyranha.logging import log
from pyranha.ui import UserInterface
from pyranha.ui.gtk.window import MainWindow


class GtkUI(UserInterface):

    def __init__(self):
        GObject.threads_init()
        Gdk.threads_init()
        super(GtkUI, self).__init__()

    def async_message(self, message_type, network=None, content=None):
        """Override the default async_message implementation to tell Gtk's main loop
        to run process_message with the given message attributes."""
        GObject.idle_add(self.process_message, (message_type, network, content))

    def run(self):
        try:
            self.window = MainWindow()
            self.window.show_all()
            Gtk.main()
        except:
            async_engine_command('stop')
            raise

    def process_message(self, (message_type, network, content)):
        if message_type == 'stopped':
            Gtk.main_quit()

        elif message_type == 'focus-entry':
            self.window.command_entry.grab_focus()

        elif message_type == 'new_channel':
            self.window.on_new_channel(network, content)

        elif message_type == 'message':
            self.window.on_message(network, content)
