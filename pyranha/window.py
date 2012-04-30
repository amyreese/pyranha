from __future__ import absolute_import, division

import os

import gtk

from pyranha.menubar import MainMenu
from pyranha.webview import Webview

html = """
<html>
<head>
    <title>Super Mega!</title>
    <style>
    * {
        box-sizing: border-box;
        margin: 0px;
        padding: 0px;
    }
    ::-webkit-scrollbar {
        width: 4px;
        height: 4px;
    }
    ::-webkit-scrollbar-track {
        background: #000;
    }
    ::-webkit-scrollbar-thumb {
        background: #f00;
    }
    </style>
</head>
<body>
    <h1>Hi There</h1>
    <p><a href="http://google.com">Google</a></p>
    <p>Dreamcatcher aute wes anderson, sustainable esse williamsburg organic. Skateboard chambray readymade est, messenger bag tumblr biodiesel hella small batch mustache locavore minim do mlkshk etsy. Sapiente scenester brooklyn, wolf irony id gentrify fanny pack food truck selvage whatever forage pour-over. Gentrify officia minim keffiyeh thundercats adipisicing incididunt, farm-to-table twee in. Master cleanse yr wayfarers, mollit bicycle rights cupidatat whatever est next level retro. Non mixtape craft beer tumblr forage. Aute pitchfork narwhal artisan anim messenger bag.</p>
    <p>Sint labore bespoke, culpa semiotics velit viral salvia. Sartorial brooklyn chambray viral ut. Minim sed assumenda authentic, trust fund freegan single-origin coffee. Mustache ut voluptate, you probably haven't heard of them banh mi jean shorts bicycle rights do trust fund echo park tempor 3 wolf moon keffiyeh authentic. Aliqua est pour-over fixie, exercitation sustainable raw denim mustache mollit banh mi. Lomo put a bird on it anim, et wes anderson PBR terry richardson carles cupidatat stumptown cred aliquip nesciunt. Farm-to-table nihil art party, gentrify ennui sriracha qui narwhal chillwave nisi four loko elit organic american apparel.</p>
    <p>Anim 8-bit ethnic, beard messenger bag mcsweeney's ennui labore fixie. Pariatur nisi fixie laboris. Non williamsburg consequat, officia next level bicycle rights lo-fi. Sunt cred raw denim excepteur, hella lo-fi aute iphone readymade incididunt. You probably haven't heard of them consectetur cosby sweater semiotics aliqua wayfarers chambray, freegan typewriter jean shorts. Vinyl odio williamsburg delectus ullamco 8-bit ad polaroid. Organic synth vice kogi 3 wolf moon williamsburg small batch.</p>
    <p>Veniam gastropub dreamcatcher PBR high life sint. Pop-up enim helvetica, organic butcher qui odd future twee 3 wolf moon. Velit quis before they sold out, banksy keytar gastropub veniam letterpress. Keffiyeh jean shorts pour-over cillum 3 wolf moon direct trade butcher. Sartorial nesciunt sed craft beer. Duis fap sed VHS thundercats. Assumenda tofu pork belly pop-up, semiotics qui commodo dolor.</p>
    <p>Sapiente duis american apparel, freegan synth consequat selvage locavore brunch exercitation. Locavore helvetica cardigan hoodie fap. Cosby sweater jean shorts put a bird on it ethical. Sint +1 direct trade, chambray ex banh mi thundercats aesthetic. Before they sold out nulla wayfarers, wolf ut Austin sriracha aesthetic. Ea wayfarers artisan bicycle rights, placeat aliqua occupy excepteur readymade echo park. Before they sold out four loko laborum, enim et consequat butcher flexitarian dolor velit nulla 3 wolf moon +1.</p>
    <p>Ennui leggings aliqua in dreamcatcher. Gluten-free post-ironic nihil master cleanse. VHS nulla ex, ennui irony semiotics cillum cred carles yr messenger bag marfa anim polaroid cliche. Yr cred williamsburg gentrify. Wes anderson messenger bag pop-up bespoke. Culpa minim selvage ut, carles portland locavore velit twee viral shoreditch. Esse dreamcatcher messenger bag, banksy gluten-free tofu brooklyn vegan nesciunt.</p>
    <p>Fugiat aute art party mlkshk, seitan culpa before they sold out mustache odd future chambray gentrify. Reprehenderit occaecat nihil, pariatur tattooed portland odio ethical delectus magna direct trade excepteur letterpress. Non swag fixie, ad chambray mustache small batch beard mixtape letterpress. Eu bespoke ad, dolor keffiyeh qui street art aliqua ullamco skateboard pinterest. Cupidatat officia consequat, pork belly proident twee fap terry richardson locavore four loko. Next level pop-up mcsweeney's, pickled bicycle rights accusamus semiotics sunt marfa consequat helvetica twee. Incididunt mollit placeat single-origin coffee, nihil cliche freegan farm-to-table swag proident gastropub chambray.</p>
</body>
</html>
"""

class MainWindow(gtk.Window):

    def __init__(self):
        gtk.Window.__init__(self)

        self.modifiers = []

        self.webview = Webview()
        self.webview.connect('title-changed', self.on_title_changed)
        self.webview.connect('load-finished', self.on_load_finished)
        self.webview.connect_after('navigation-requested', self.on_navigation_requested)

        main_menu = MainMenu()
        self.add_accel_group(main_menu.accelerators)

        vbox = gtk.VBox(homogeneous=False, spacing=0)
        vbox.pack_start(main_menu, expand=False, fill=True, padding=0)

        self.scroller = gtk.ScrolledWindow()
        # TODO: figure out why this doesn't work
        self.scroller.set_policy(gtk.POLICY_NEVER, gtk.POLICY_NEVER)
        self.scroller.add(self.webview)

        vbox.pack_start(self.scroller, expand=True, fill=True, padding=0)

        self.command_entry = gtk.TextView()
        self.command_entry.set_property('wrap-mode', gtk.WRAP_WORD)
        #self.command_entry.connect('key-press-event', self.on_command_keydown)
        self.command_entry.connect('key-release-event', self.on_command_keyup)
        vbox.pack_start(self.command_entry, expand=False, fill=True, padding=0)

        self.add(vbox)
        self.set_default_size(900, 400)
        self.show_all()

        self.webview.load_string(html, "text/html", "iso-8895-15", "about")
        self.command_entry.grab_focus()

    def on_command_keyup(self, widget, event):
        if not len(event.state.value_names):
            if event.keyval == 65293: #enter
                text_buffer = widget.get_buffer()
                command = text_buffer.get_text(text_buffer.get_start_iter(), text_buffer.get_end_iter()).strip()
                print 'command: ', command
                text_buffer.set_text('')

    def on_navigation_requested(self, widget, frame, request):
        uri = request.get_uri()
        print 'uri: ' + uri

        if uri == 'about':
            return 0
        else:
            os.system('xdg-open ' + uri)
            return 1

    def on_load_finished(self, widget, frame):
        self.webview.move_cursor(gtk.MOVEMENT_BUFFER_ENDS, 1)

    def on_title_changed(self, widget, frame, title):
        print 'title: ' + title

def init():
    window = MainWindow()
    window.connect('delete-event', gtk.main_quit)
    window.show_all()
    gtk.main()
