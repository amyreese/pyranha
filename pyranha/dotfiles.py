from __future__ import absolute_import, division

import os
from os import path

# load YAML, and default to using libYAML whenever possible
import yaml
try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    print 'falling back to pure python yaml'
    from yaml import SafeLoader, SafeDumper

# Default dotfile path
defaultfilepath = path.join(path.dirname(path.realpath(__file__)), 'dotfiles')

# Check the user's .pyranha and create it if needed
dotfilepath = path.expanduser('~/.pyranha')
if path.exists(dotfilepath):
    if not path.isdir(dotfilepath):
        raise IOError('pyranha dotfile path {0} exists but is not a directory'.format(dotfilepath))
else:
    os.mkdir(dotfilepath)


def load(filename):
    """Load the given filename and return the resulting object."""
    with open(filename) as f:
        return yaml.load(f.read(), Loader=SafeLoader)

def save(filename, obj):
    """Write the given object to the given filename."""
    with open(filename, 'w') as f:
        return f.write(yaml.dump(obj, default_flow_style=False, Dumper=SafeDumper))

def merge(current, new, merge_new_keys=False):
    """Recursively merge two dictionaries, overwriting values in current with values in new.
    Keys in new that don't already exist will only be added to current if merge_new_keys is True."""
    for key in list(new.keys()):
        new_value = new[key]

        if key in current:
            current_value = current[key]

            if type(current_value) != type(new_value):
                continue # TODO: handle type mismatch

            if type(new_value) == dict:
                new_value = merge(dict(current_value), dict(new_value))

            current[key] = new_value

        elif merge_new_keys:
            current[key] = new_value

    return current


class Dotfile(object):
    """Dictionary-based structure backed by an on-disk, YAML-formatted config file.
    The user's dotfile is watched for updates, and changes are read automatically at next dictionary access."""

    def __init__(self, name, use_defaults=True):
        """Initialize a new dotfile object with the given name.
        If use_defaults is enabled, default values will be populated from `pyranha/dotfiles/<name>.yaml`.
        If use_defaults is disabled and the user's dotfile doesn't exist, the defaults will be loaded anyways."""

        self.name = name
        self.defaultfile = path.join(defaultfilepath, name + '.yaml')
        self.dotfile = path.join(dotfilepath, name)

        self.use_defaults = use_defaults
        self.values = {}
        self.m_time = 0.0

        self.load(fresh=True)

    def load(self, fresh=False):
        """Load dotfile values from disk if the file has changed since last m_time.
        If fresh is true, any existing values will be discarded."""
        user_values = None

        if path.exists(self.dotfile):
            m_time = os.stat(self.dotfile).st_mtime
            if m_time > self.m_time:
                user_values = load(self.dotfile)
                self.m_time = m_time

        if fresh:
            self.values.clear()

            if (self.use_defaults or user_values is None) and path.exists(self.defaultfile):
                self.values = load(self.defaultfile)

        if user_values is not None:
            self.values = merge(self.values, user_values, merge_new_keys=(not self.use_defaults))

    def save(self):
        """Save current dotfile values to disk, and update m_time."""
        save(self.dotfile, self.values)
        self.m_time = os.stat(self.dotfile).st_mtime

    def __repr__(self):
        return '<Dotfile {0}: {1}>'.format(self.name, self.values.__repr__())

    ### dict view method mappings ###

    def __len__(self):
        self.load()
        return self.values.__len__()

    def __contains__(self, item):
        self.load()
        return self.values.__contains__(item)

    def __getitem__(self, key):
        self.load()
        return self.values.__getitem__(key)

    def __iter__(self):
        self.load()
        return self.values.__iter__()

    def keys():
        self.load()
        return self.values.keys()

    ### dict modify method mappings ###

    def __setitem__(self, key, value):
        self.load()
        rv = self.values.__setitem__(key, value)
        self.save()
        return rv

    def __delitem__(self, key):
        self.load()
        rv = self.values.__delitem__(key)
        self.save()
        return rv

    def update(self, *args, **kwargs):
        self.load()
        rv = self.values.update(*args, **kwargs)
        self.save()
        return rv

    def setdefault(self, key, value=None):
        self.load()
        rv = self.values.setdefault(key, value)
        self.save()
        return rv
