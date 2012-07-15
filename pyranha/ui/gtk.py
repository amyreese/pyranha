# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import async_engine_command
from pyranha.ui import UserInterface

css = """\
GtkNotebook tab GtkLabel.new_messages {
    color: #ff0000;
}
GtkNotebook tab:first-child {
    -tab-curvature: 0;
    -initial-gap: 10;
    -GtkNotebook-tab-curvature: 0;
    -GtkNotebook-initial-gap: 10;
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

class MainWindow(Gtk.Window):

    def __init__(self):
        super(Gtk.Window, self).__init__()
        self.connect('show', self.start)
        self.connect('delete-event', self.stop)

        self.css_provider = Gtk.CssProvider()
        self.css_provider.load_from_data(css)
        #Gtk.StyleContext.add_provider_for_screen(Gdk.Screen.get_default(), self.css_provider, 900)
        #self.style_context.add_provider(self.css_provider, 900)

        main_menu = MainMenu()
        self.add_accel_group(main_menu.accelerators)

        vbox = Gtk.VBox(homogeneous=False, spacing=0)
        vbox.pack_start(main_menu, expand=False, fill=True, padding=0)

        self.notebook = Gtk.Notebook()
        self.notebook.set_show_border(False)
        self.notebook.set_scrollable(True)

        self.scroller = Gtk.ScrolledWindow()
        # TODO: figure out why this doesn't work
        #self.scroller.set_policy(Gtk.PolicyType.NEVER, Gtk.PolicyType.NEVER)

        self.content_box = Gtk.VBox(homogeneous=False, spacing=0)
        self.scroller.add_with_viewport(self.content_box)

        self.notebook.append_page(self.scroller, Gtk.Label('freenode'))
        self.notebook.append_page(Gtk.ScrolledWindow(), Gtk.Label('#foo'))
        self.notebook.append_page(Gtk.ScrolledWindow(), Gtk.Label('#pyranha'))
        self.notebook.append_page(Gtk.ScrolledWindow(), Gtk.Label('ea2d'))
        self.notebook.append_page(Gtk.ScrolledWindow(), Gtk.Label('#boring'))
        self.notebook.append_page(Gtk.ScrolledWindow(), Gtk.Label('#pyranha'))

        vbox.pack_start(self.notebook, expand=True, fill=True, padding=0)

        self.command_entry = Gtk.TextView()
        self.command_entry.set_property('wrap-mode', Gtk.WrapMode.WORD)
        self.command_entry.connect('key-press-event', self.on_command_keydown)
        #self.command_entry.connect('key-release-event', self.on_command_keyup)
        vbox.pack_start(self.command_entry, expand=False, fill=True, padding=0)

        self.add(vbox)
        self.set_default_size(900, 400)
        self.show_all()

        self.command_entry.grab_focus()

    def on_command_keydown(self, widget, event):
        if not len(event.state.value_names):
            if event.keyval == 65293: #enter
                text_buffer = widget.get_buffer()
                command = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter(), True).strip()
                print 'command: ', command
                text_buffer.set_text('')
                return True

    def start(self, widget):
        async_engine_command('connect')

    def stop(self, widget, event):
        async_engine_command('stop')

class MainMenu(Gtk.MenuBar):

    def __init__(self):
        Gtk.MenuBar.__init__(self)

        self.accelerators = Gtk.AccelGroup()
        self.append(self.file_menu())

    def file_menu(self):
        menu = Gtk.Menu()

        quit_item = Gtk.MenuItem('Quit')
        quit_item.add_accelerator('activate',
                                  self.accelerators,
                                  ord('Q'),
                                  Gdk.ModifierType.CONTROL_MASK,
                                  Gtk.AccelFlags.VISIBLE)
        quit_item.connect('activate', self.on_quit)
        menu.append(quit_item)

        menu_item = Gtk.MenuItem('File')
        menu_item.set_submenu(menu)

        return menu_item

    def on_quit(self, widget):
        async_engine_command('stop')
