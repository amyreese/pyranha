# Copyright (c) 2012 John Reese
# Licensed under the MIT License

from __future__ import absolute_import, division

import re

# load YAML, and default to using libYAML whenever possible
import yaml
try:
    from yaml import CSafeLoader as SafeLoader, CSafeDumper as SafeDumper
except ImportError:
    from yaml import SafeLoader, SafeDumper

document_marker = re.compile('^---\w*$', re.M)

def load(filename, supplement=False):
    """Load the given filename and return the resulting object."""
    with open(filename) as f:
        if supplement:
            data = f.read()
            doc, sup = document_marker.split(data, 1)
            doc = yaml.load(doc, Loader=SafeLoader)
            if type(doc) != dict:
                doc = {}
            return doc, sup
        else:
            doc = yaml.load(f.read(), Loader=SafeLoader)
            if type(doc) != dict:
                doc = {}
            return doc

def save(filename, obj, supplement=None):
    """Write the given object to the given filename."""
    with open(filename, 'w') as f:
        if supplement is not None:
            f.write(yaml.dump(obj, default_flow_style=False, Dumper=SafeDumper))
            f.write('\n---\n')
            f.write(supplement)
        else:
            f.write(yaml.dump(obj, default_flow_style=False, Dumper=SafeDumper))
