Theming
=======

This document is a simple introduction to theming Pyranha.


Overview
--------

Pyranha uses Gtk+ version 3 for widgets, which offers a stripped down version
of CSS for theming widgets [<sup>1</sup>][1].  Pyranha piggybacks on this mechanism to provide a
simple and familiar method for styling the application.  Themes consist of a
single CSS file, with a custom YAML header providing metadata for the theme.

Pyranha also provides a built-in "reset" theme that is included by default with
every theme, which removes all styling provided by the user or system Gtk theme.
An empty "native" theme is also included which contains no CSS at all, for users
that prefer a generic look and feel for the application.

Themes should be located in either the user's `~/.pyranha/themes/` directory, or
bundled with Pyranha in `pyranha/pyranha/themes/`.


Header
------

The theme header is a simple, explicit YAML document, with the following values,
all of which are optional:

*   `name` - a user-friendly title for the theme, defaulting to the filename
*   `description` - a description of the theme, defaulting to blank
*   `author` - the author of the theme, with any url or contact information,
    defaulting to blank
*   `reset` - a boolean value for whether the reset style should be included in
    the theme's CSS, defaulting to true

The header must be separated from the CSS by the YAML document marker, `---`.


Example: `native.css`

    name: Native
    description: A theme that does nothing
    author: Some bloke from Ken-tucky
    reset: false
    ---
    /* No CSS here */


[1]: http://developer.gnome.org/gtk3/stable/GtkCssProvider.html#GtkCssProvider.description "GtkCSSProvider"
