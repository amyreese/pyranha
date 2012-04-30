from __future__ import absolute_import, division

import gtk
from gtk import gdk, AccelGroup, Menu, MenuBar, MenuItem

class MainMenu(MenuBar):

    def __init__(self):
        MenuBar.__init__(self)

        self.accelerators = AccelGroup()

        self.append(self.file_menu())

    def file_menu(self):
        menu = Menu()

        quit_item = MenuItem('Quit')
        quit_item.add_accelerator('activate',
                                  self.accelerators,
                                  ord('Q'),
                                  gdk.CONTROL_MASK,
                                  gtk.ACCEL_VISIBLE)
        quit_item.connect('activate', self.on_quit)
        menu.append(quit_item)

        menu_item = MenuItem('File')
        menu_item.set_submenu(menu)

        return menu_item


    def on_quit(self, widget):
        gtk.main_quit()
