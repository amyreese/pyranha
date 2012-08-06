# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import time

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command, async_ui_message
from pyranha.dotfiles import Dotfile
from pyranha.engine.listener import Listener
from pyranha.keymap import Keymap
from pyranha.logging import log
from pyranha.ui.gtk.theme import themes, load_themes

class MainWindow(Gtk.Window):

    def __init__(self):
        super(Gtk.Window, self).__init__()
        self.connect('show', self.start)
        self.connect('delete-event', self.stop)

        self.css_provider = None

        self.channel_box = Gtk.Box(homogeneous=False, spacing=0)

        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        vbox.pack_start(self.channel_box, expand=True, fill=True, padding=0)

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

        self.network_channels = {}
        self.current_channel = None

    def on_focus_out(self, widget, event):
        self.command_entry.grab_focus()

    def on_command_keydown(self, widget, event):
        command = self.keymap.gtk_event(event)

        if command is None:
            return False

        log.info('key command: {0}'.format(command))

        if command == 'send-buffer':
            text_buffer = self.command_entry.get_buffer()
            message = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
            log.info('message: {0}'.format(message))

            channel_window = self.current_channel
            async_engine_command('send', channel_window.network, (channel_window.channel, message))
            text_buffer.set_text('')
            return True

        elif command == 'window-next':
            l = []
            for n in self.network_channels:
                for c in self.network_channels[n]:
                    l.append(self.network_channels[n][c])

            p = l.index(self.current_channel) + 1
            if p == len(l):
                self.set_channel(l[0])
            else:
                self.set_channel(l[p])

        elif command == 'window-previous':
            l = []
            for n in self.network_channels:
                for c in self.network_channels[n]:
                    l.append(self.network_channels[n][c])

            p = l.index(self.current_channel) - 1
            if p < 0:
                self.set_channel(l[-1])
            else:
                self.set_channel(l[p])

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

    def set_channel(self, channel_window):
        log.debug('setting channel to {0}'.format(channel_window))
        if self.current_channel is not None:
            self.channel_box.remove(self.current_channel)

        self.current_channel = channel_window
        self.channel_box.pack_start(channel_window, expand=True, fill=True, padding=0)

    def on_new_channel(self, network, channel):
        log.debug('in on_new_channel')
        if network.name not in self.network_channels:
            self.network_channels[network.name] = {}

        if channel.name not in self.network_channels[network.name]:
            channel_window = ChannelWindow(network, channel)
            self.network_channels[network.name][channel.name] = channel_window

        if self.current_channel is None:
            self.set_channel(channel_window)

    def on_message(self, network, channel):
        log.debug('in on_message')
        if network.name in self.network_channels and channel.name in self.network_channels[network.name]:
            channel_window = self.network_channels[network.name][channel.name]
            channel_window.on_message(network, channel)

        else:
            log.warning('message for unknown channel {0}'.format(channel.name))

class ChannelWindow(Gtk.HBox):
    def __init__(self, network, channel):
        super(Gtk.HBox, self).__init__(homogeneous=False, spacing=0)
        self.network = network
        self.channel = channel

        self.scroller = Gtk.ScrolledWindow()

        self.grid_height = 0
        self.grid = Gtk.Grid()
        self.grid.connect('size-allocate', self.grid_resized)

        self.scroller.add_with_viewport(self.grid)
        self.scroller.set_vadjustment(Gtk.Adjustment())

        self.pack_start(self.scroller, expand=True, fill=True, padding=0)

        self.listmodel = Gtk.ListStore(str, str)
        self.listmodel.append(['@','foobot'])
        self.listmodel.append(['+','someguy'])
        self.listmodel.append(['','h8rgonnah8'])

        self.listview = Gtk.TreeView(self.listmodel)
        self.listview.set_headers_visible(False)
        self.listrenderer = Gtk.CellRendererText()
        self.listview.append_column(Gtk.TreeViewColumn('', self.listrenderer, text=0))
        self.listview.append_column(Gtk.TreeViewColumn('', self.listrenderer, text=1))
        self.listview.connect('row-activated', self.listview_clicked)

        self.pack_start(self.listview, expand=False, fill=True, padding=0)
        self.show_all()

    def grid_resized(self, widget, rectangle):
        adj = self.scroller.get_vadjustment()
        adj.set_value(adj.get_upper())

    def listview_clicked(self, widget, path, column):
        pass

    def on_message(self, network, channel):
        timestamp, source, message = channel.messages[-1]
        if source is None:
            source = ''

        timelabel = Gtk.Label()
        timelabel.set_selectable(True)
        timelabel.set_line_wrap(False)
        timelabel.set_alignment(0,0)
        timelabel.set_text(time.strftime('%H:%I' ,time.localtime(timestamp)))
        timelabel.show()

        sourcelabel = Gtk.Label()
        sourcelabel.set_selectable(True)
        sourcelabel.set_line_wrap(True)
        sourcelabel.set_alignment(0,0)
        sourcelabel.set_text(source)
        sourcelabel.show()

        msglabel = Gtk.Label()
        msglabel.set_selectable(True)
        msglabel.set_line_wrap(True)
        msglabel.set_alignment(0,0)
        msglabel.set_text(message)
        msglabel.show()

        self.grid.attach(timelabel, 0, self.grid_height, 1, 1)
        self.grid.attach(sourcelabel, 1, self.grid_height, 1, 1)
        self.grid.attach(msglabel, 2, self.grid_height, 1, 1)
