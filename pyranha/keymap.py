# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

from pyranha.dotfiles import Dotfile


class Keymap(object):
    def __init__(self):
        self.keymap = Dotfile('keymap')

    def map_command(self, code):
        if code == '':
            return None

        if code == 'Enter':
            return 'send-buffer'

        command = self.keymap.get(code)
        if type(command) == str:
            return command

        return None

    def gtk_event(self, event):
        """Very simple and dirty method for generating a vi-like key binding from a given keypress event."""
        from gi.repository import Gdk

        k = event.hardware_keycode
        v = event.keyval
        m = event.state
        s = event.string

        code = ''

        if m & Gdk.ModifierType.CONTROL_MASK:
            code += 'C-'
        if m & Gdk.ModifierType.SUPER_MASK:
            code += 'S-'
        if m & Gdk.ModifierType.META_MASK:
            code += 'M-'

        if (v >= 65 and v <= 90) or (v >= 97 and v <= 122) or \
            (v >= 48 and v <= 57) or (v >= 33 and v <= 41):
            code += chr(v)
        else:
            if m & Gdk.ModifierType.SHIFT_MASK:
                code += '^-'

            if k == 23:
                code += 'Tab'
            elif k == 36:
                code += 'Enter'
            elif k == 111:
                code += 'Up'
            elif k == 112:
                code += 'PgUp'
            elif k == 113:
                code += 'Left'
            elif k == 114:
                code += 'Right'
            elif k == 116:
                code += 'Down'
            elif k == 117:
                code += 'PgDn'

            else:
                code += str(k)

        return self.map_command(code)
