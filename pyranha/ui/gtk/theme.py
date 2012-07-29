# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import os
from os import path

from gi.repository import Gdk, Gtk, GLib, GObject

from pyranha import installpath, userpath
from pyranha.yaml import load, save

themes = {}

class Theme(object):
    def __init__(self, id, metadata, source):
        self.id = id
        self.name = metadata.get('name', id)
        self.description = metadata.get('description', '')
        self.author = metadata.get('author', '')
        self.reset = metadata.get('reset', True)
        self.source = source

    def render(self):
        css = ''

        if self.reset and 'reset' in themes:
            css += themes['reset'].source

        css += self.source
        return css

def load_themes():
    global themes

    themes.clear()
    themelist = []

    for root, dirs, files in os.walk(path.join(installpath, 'themes')):
        for filename in files:
            f, ext = path.splitext(filename)
            if ext == '.css':
                themelist.append((f, path.join(root, filename)))

    for root, dirs, files in os.walk(path.join(userpath, 'themes')):
        for filename in files:
            f, ext = path.splitext(filename)
            if ext == '.css':
                themelist.append((f, path.join(root, filename)))

    for id, filepath in themelist:
        metadata, source = load(filepath, supplement=True)
        themes[id] = Theme(id, metadata, source)

    return True
