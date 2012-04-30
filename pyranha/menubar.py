from __future__ import absolute_import, division

from gi.repository import Gtk, Gdk

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
        Gtk.main_quit()
