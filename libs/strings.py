"""
libs.strings

By default, uses the 'en-gb.json' file inside the strings folder.

If language changes, set 'libs.strings.default_locale' and run 'libs.strings.refresh()'
"""
import json

default_locale = 'en-gb'
cached_strings = {}


def refresh():
    """
    Reload the strings from the setted file.
    """
    print('refreshing')
    global cached_strings
    with open(f"./strings/{default_locale}.json") as file:
        cached_strings = json.load(file)


def gettext(name):
    """
    Access cached strings and return the value from a given key.
    Example: gettext("user_activated")
    """
    return cached_strings[name]


refresh()  # Refresh cached strings when this lib is loaded.
