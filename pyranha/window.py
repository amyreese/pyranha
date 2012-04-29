from __future__ import absolute_import, division

from pyranha import filepath
import gtk
import webkit

html = """
<html><head><title>Super Mega!</title></head><body><h1>Hi There</h1><p><a href="http://google.com">Google</a></p></body></html>
"""

class MainWindow(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        self.scroller = gtk.ScrolledWindow()
        self.webview = webkit.WebView()
        self.webview.connect('title-changed', self.on_title_changed)
        self.webview.connect_after('navigation-requested', self.on_navigation_requested)
        #self.webview.connect('', self.)

        self.scroller.add(self.webview)
        self.add(self.scroller)

        self.set_default_size(800, 600)
        self.webview.load_string(html, "text/html", "iso-8895-15", "about")


    def on_navigation_requested(self, widget, frame, request):
        uri = request.get_uri()
        if uri == 'about':
            return 0
        else:
            print 'uri: ' + uri
            return 1

    def on_title_changed(self, widget, frame, title):
        print 'new title: ' + title

def init():
    # css = Gtk.CssProvider()
    # with open(filepath('css', 'pyranha.css')) as f:
    #     css.load_from_data(f.read())

    # screen = Gdk.Screen.get_default()
    # context = Gtk.StyleContext()
    # context.add_provider_for_screen(screen, css, Gtk.STYLE_PROVIDER_PRIORITY_USER)

    window = MainWindow()
    window.connect('delete-event', gtk.main_quit)
    window.show_all()
    gtk.main()
