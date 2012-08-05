# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command, async_ui_message
from pyranha.dotfiles import Dotfile
from pyranha.keymap import Keymap
from pyranha.logging import log
from pyranha.ui.gtk.theme import themes, load_themes

class MainWindow(Gtk.Window):

    def __init__(self):
        super(Gtk.Window, self).__init__()
        self.connect('show', self.start)
        self.connect('delete-event', self.stop)

        self.css_provider = None

        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        hbox = Gtk.HBox(homogeneous=False, spacing=0)

        self.scroller = Gtk.ScrolledWindow()

        self.content_box = Gtk.VBox(homogeneous=False, spacing=0)
        self.content_box.connect('size-allocate', self.channel_resized)
        self.scroller.add_with_viewport(self.content_box)
        self.scroller.set_vadjustment(Gtk.Adjustment())

        hbox.pack_start(self.scroller, expand=True, fill=True, padding=0)

        self.listmodel = Gtk.ListStore(str)
        self.listmodel.append(['@foobot'])
        self.listmodel.append(['+someguy'])
        self.listmodel.append(['h8rgonnah8'])

        self.listview = Gtk.TreeView(self.listmodel)
        self.listview.set_headers_visible(False)
        renderer = Gtk.CellRendererText()
        self.listview.append_column(Gtk.TreeViewColumn('#somechan', renderer, text=0))
        self.listview.connect('row-activated', self.listview_clicked)

        hbox.pack_start(self.listview, expand=False, fill=True, padding=0)
        vbox.pack_start(hbox, expand=True, fill=True, padding=0)

        self.command_entry = Gtk.TextView()
        self.command_entry.set_property('wrap-mode', Gtk.WrapMode.WORD)
        #self.command_entry.connect('key-press-event', self.on_command_keydown)
        self.connect('key-press-event', self.on_command_keydown)
        vbox.pack_start(self.command_entry, expand=False, fill=True, padding=0)

        self.add(vbox)
        self.set_default_size(900, 400)
        self.show_all()

        self.command_entry.grab_focus()
        self.keymap = Keymap()

        self.update_theme()

    def channel_resized(self, widget, rectangle):
        adj = self.scroller.get_vadjustment()
        adj.set_value(adj.get_upper())

    def listview_clicked(self, widget, path, column):
        text_buffer = self.command_entry.get_buffer()
        message = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
        message = '/msg nick ' + message
        text_buffer.set_text(message)

        async_ui_message('focus-entry')

    def on_focus_out(self, widget, event):
        self.command_entry.grab_focus()

    def on_command_keydown(self, widget, event):
        command = self.keymap.gtk_event(event)

        if command is None:
            return False

        elif command == 'send-buffer':
            text_buffer = self.command_entry.get_buffer()
            message = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
            log.info('message: {0}'.format(message))
            async_engine_command('raw', '*', message)
            text_buffer.set_text('')
            return True

        elif command == 'quit':
            self.stop()

        else:
            method = command.replace('-', '_')
            method = getattr(self, method, None)
            if method is not None:
                method()

        return True

    def start(self, widget):
        async_engine_command('connect')

    def stop(self, widget=None, event=None):
        async_engine_command('stop')

    def update_theme(self):
        load_themes()
        config = Dotfile('config')

        theme = config['theme']
        if theme not in themes:
            log.warning('configured theme "{0}" not found; falling back to native'.format(theme))
            theme = 'native'

        theme = themes[theme]
        css = theme.render()

        if self.css_provider is not None:
            Gtk.StyleContext.remove_provider_for_screen(Gdk.Screen.get_default(), self.css_provider)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(css)
        Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider, 900)
