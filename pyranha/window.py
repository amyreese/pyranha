from __future__ import absolute_import, division

from gi.repository import Gtk

class MainWindow(Gtk.Window):

    def __init__(self):
        Gtk.Window.__init__(self, title="Pyranha")

        self.button = Gtk.Button(label="Do Something")
        self.button.connect('clicked', self.on_click)
        self.add(self.button)

    def on_click(self, widget):
        print 'Something'


def init():
    window = MainWindow()
    window.connect('delete-event', Gtk.main_quit)
    window.show_all()
    Gtk.main()
