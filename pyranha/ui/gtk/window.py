# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command
from pyranha.dotfiles import Dotfile
from pyranha.keymap import Keymap

css = """\
* {
    background: #ffffff;
    color: #000000;
    margin: 0;
    padding: 0;
    font-size: 10;
}
"""

class MainWindow(Gtk.Window):

    def __init__(self):
        super(Gtk.Window, self).__init__()
        self.connect('show', self.start)
        self.connect('delete-event', self.stop)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider, 900)

        vbox = Gtk.VBox(homogeneous=False, spacing=0)

        self.scroller = Gtk.ScrolledWindow()

        self.content_box = Gtk.VBox(homogeneous=False, spacing=0)
        self.scroller.add_with_viewport(self.content_box)

        vbox.pack_start(self.scroller, expand=True, fill=True, padding=0)

        self.command_entry = Gtk.TextView()
        self.command_entry.set_property('wrap-mode', Gtk.WrapMode.WORD)
        self.command_entry.connect('key-press-event', self.on_command_keydown)
        self.command_entry.connect('focus-out-event', self.on_focus_out)
        vbox.pack_start(self.command_entry, expand=False, fill=True, padding=0)

        self.add(vbox)
        self.set_default_size(900, 400)
        self.show_all()

        self.command_entry.grab_focus()
        self.keymap = Keymap()

    def on_focus_out(self, widget, event):
        self.command_entry.grab_focus()

    def on_command_keydown(self, widget, event):
        command = self.keymap.gtk_event(event)

        if command is None:
            return False

        elif command == 'send-buffer':
            text_buffer = widget.get_buffer()
            message = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
            print 'message: ', message
            text_buffer.set_text('')
            return True

        elif command == 'quit':
            self.stop(None, None)

        return True

    def start(self, widget):
        async_engine_command('connect')

    def stop(self, widget=None, event=None):
        async_engine_command('stop')
