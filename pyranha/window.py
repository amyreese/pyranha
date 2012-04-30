from __future__ import absolute_import, division

import os

import gtk

from pyranha.menubar import MainMenu
from pyranha.webview import Webview

with open('prototype.html') as f:
    html = f.read()

class MainWindow(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        self.webview = Webview()
        self.webview.connect('title-changed', self.on_title_changed)
        self.webview.connect('load-finished', self.on_load_finished)
        self.webview.connect_after('navigation-requested', self.on_navigation_requested)

        main_menu = MainMenu()
        self.add_accel_group(main_menu.accelerators)

        vbox = gtk.VBox(homogeneous=False, spacing=0)
        vbox.pack_start(main_menu, expand=False, fill=True, padding=0)

        self.scroller = gtk.ScrolledWindow()
        # TODO: figure out why this doesn't work
        self.scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        self.scroller.add(self.webview)

        vbox.pack_start(self.scroller, expand=True, fill=True, padding=0)

        self.command_entry = gtk.TextView()
        self.command_entry.set_property('wrap-mode', gtk.WRAP_WORD)
        self.command_entry.connect('key-press-event', self.on_command_keydown)
        #self.command_entry.connect('key-release-event', self.on_command_keyup)
        vbox.pack_start(self.command_entry, expand=False, fill=True, padding=0)

        self.add(vbox)
        self.set_default_size(900, 400)
        self.show_all()

        self.webview.load_string(html, "text/html", "iso-8895-15", "about")
        self.command_entry.grab_focus()

    def on_command_keydown(self, widget, event):
        if not len(event.state.value_names):
            if event.keyval == 65293: #enter
                text_buffer = widget.get_buffer()
                command = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter()).strip()
                print 'command: ', command
                text_buffer.set_text('')
                return gtk.TRUE

    def on_navigation_requested(self, widget, frame, request):
        uri = request.get_uri()
        print 'uri: ' + uri

        if uri == 'about':
            return 0
        else:
            os.system('xdg-open ' + uri)
            return 1

    def on_load_finished(self, widget, frame):
        pass

    def on_title_changed(self, widget, frame, title):
        print 'title: ' + title

def init():
    window = MainWindow()
    window.connect('delete-event', gtk.main_quit)
    window.show_all()
    gtk.main()
