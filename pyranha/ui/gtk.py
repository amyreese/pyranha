# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command
from pyranha.ui import UserInterface

css = """\
* {
    background: #ffffff;
    color: #000000;
    margin: 0;
    padding: 0;
    font-size: 10;
}
"""

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
        label.set_markup(message)
        label.show()
        self.window.content_box.pack_start(label, expand=False, fill=False, padding=0)

        if message_type == 'stopped':
            Gtk.main_quit()

def vicode(event):
    """Very simple and dirty method for generating a vi-like key binding from a given keypress event."""
    k = event.hardware_keycode
    v = event.keyval
    m = event.state
    s = event.string

    result = ''

    if m & Gdk.ModifierType.CONTROL_MASK:
        result += 'C-'
    if m & Gdk.ModifierType.SUPER_MASK:
        result += 'S-'
    if m & Gdk.ModifierType.META_MASK:
        result += 'M-'

    if (v >= 65 and v <= 90) or (v >= 97 and v <= 122) or \
        (v >= 48 and v <= 57) or (v >= 33 and v <= 41):
        result += chr(v)
    else:
        if m & Gdk.ModifierType.SHIFT_MASK:
            result += '^-'

        if k == 23:
            result += 'Tab'
        elif k == 36:
            result += 'Enter'
        elif k == 112:
            result += 'PgUp'
        elif k == 117:
            result += 'PgDn'

        else:
            return ''

    return result


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

    def on_command_keydown(self, widget, event):
        code = vicode(event)

        if code == '':
            return False

        if code == 'Enter':
            text_buffer = widget.get_buffer()
            command = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
            print 'command: ', command
            text_buffer.set_text('')
            return True

        if code == 'C-q':
            self.stop(None, None)
            return True

        return False

    def start(self, widget):
        async_engine_command('connect')

    def stop(self, widget=None, event=None):
        async_engine_command('stop')
