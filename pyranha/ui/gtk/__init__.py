# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command
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
        print 'queueing idle_add: {0}, {1}, {2}'.format(message_type, network, content)
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
        message = 'in process_message: {0}, {1}, {2}'.format(message_type, network, content)
        label = Gtk.Label()
        label.set_selectable(True)
        label.set_line_wrap(True)
        label.set_alignment(0,0)
        label.set_markup(message)
        label.show()
        self.window.content_box.pack_start(label, expand=False, fill=False, padding=0)

        if message_type == 'stopped':
            Gtk.main_quit()

        elif message_type == 'focus-entry':
            self.window.command_entry.grab_focus()
