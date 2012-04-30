from __future__ import absolute_import, division

import os

import gobject
import gtk
import webkit

class Settings(webkit.WebSettings):
    def __init__(self):
        webkit.WebSettings.__init__(self)

        overrides = {
            'default-font-family': 'sans-serif',
            'default-font-size': 12,
            'enable-accelerated-compositing': True,
            'enable-developer-extras': False,
            'enable-dns-prefetching': False,
            'enable-frame-flattening': True,
            'enable-html5-database': False,
            'enable-html5-local-storage': False,
            'enable-java-applet': False,
            'enable-offline-web-application-cache': False,
            'enable-page-cache': False,
            'enable-plugins': False,
            'enable-scripts': True,
            'enable-spell-checking': True,
            'resizable-text-areas': False,
            'tab-key-cycles-through-elements': False,
            'user-agent': 'Pyranha IRC webkit',
        }

        for key in overrides:
            self.set_property(key, overrides[key])

class Webview(webkit.WebView):

    def __init__(self):
        props = {'self-scrolling': True}
        gobject.GObject.__gobject_init__(self, **props)
        webkit.WebView.__init__(self)

        self.set_property('can-focus', False)

        self.set_settings(Settings())
