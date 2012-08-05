# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import logging
from logging import Formatter, FileHandler, StreamHandler
from os import path

from pyranha import userpath
from pyranha.dotfiles import Dotfile

config = Dotfile('config')
format = Formatter('[%(asctime)s] %(levelname)7s: %(message)s')

log = logging.getLogger('pyranha')
log.setLevel(logging.WARNING)

error = FileHandler(path.join(userpath, 'error.log'))
error.setLevel(logging.WARNING)
error.setFormatter(format)
log.addHandler(error)

if config['debug']:
    format = Formatter('[%(asctime)s] %(levelname)7s %(module)s.%(funcName)s.%(lineno)s: %(message)s')
    log.setLevel(logging.DEBUG)
    debug = FileHandler(path.join(userpath, 'debug.log'))
    debug.setLevel(logging.DEBUG)
    debug.setFormatter(format)
    log.addHandler(debug)

console = StreamHandler()
console.setLevel(logging.DEBUG)
console.setFormatter(format)
log.addHandler(console)

