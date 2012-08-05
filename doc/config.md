Configuration
=============

This document covers all configuration options for Pyranha.

Overview
--------

Configuration files for Pyranha use [YAML][] for the file format.  All
configuration files consist of a top-level dictionary.  Key values may be one of
the following:

* boolean values (true or false)
* integer values
* string values
* list of values, consisting of the above value types, all of the same type
* nested dictionary consisting of the above value types

Note that this means that keys can contain a nested dictionary, but cannot
contain a list of dictionaries.  This is to simplify processing, as well as to
eliminate confusion when reading or writing configurations.

When configuration files are first loaded, the global configuration is loaded,
and user configuration is merged into the global configuration, overriding
default values.  Options that do not exist in the global configuration will be
discarded from user configuration when loaded.

Global (default) configurations are stored in the installation path for Pyranha,
while user (override) configurations are stored in `$HOME/.pyranha`, though this
may vary in the future depending on platform.


.pyranha/config
---------------

This configuration file covers the most basic options, and lists the default
value for each option.

*   `debug: false`

    When false, warnings and errors are logged to `.pyranha/error.log`.  When
    true, more output is generated, and more detailed messages are logged to
    `.pyranha/debug.log`.

*   `theme: native`

    Name of the theme to use.


.pyranha/keymap
---------------


.pyranha/networks
-----------------



[YAML]: http://www.yaml.org/
