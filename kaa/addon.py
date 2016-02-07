""" Utility functions for kaa customization."""

from kaa.keyboard import *
import kaa.command
import kaa.config


def setup(filemode='kaa.filetype.default.defaultmode.DefaultMode'):
    assert isinstance(filemode, str)

    def _f(f):
        add_class_addon(filemode, 'setup', f)
        return f
    return _f


# Dict to register mode class addon.
# Mode class fetches addon functions form this dict.
_class_addons = {}


def add_class_addon(classname, key, value):
    """Register class addon"""

    d = _class_addons.setdefault(classname, {})
    d.setdefault(key, []).append(value)


def get_addon(name, key, default=()):
    """Get class addon"""
    d = _class_addons.get(name, None)
    if d:
        return d.get(key, default)
    return default


def keybind(filemode='kaa.filetype.default.defaultmode.DefaultMode',
            editmode='input', keymap=None):
    """Register keybind.

    filemode -- Mode class name to register keybind.
                  (default 'kaa.filetype.default.defaultmode.DefaultMode)
    editmode -- Editmode to register keybind.
                  Valid values are:'insert', 'command', 'visual', 'visualline'.
                  (default 'input')

    keymap -- Dictionary of keybind and command name.

    ex)
        keybind(
             filemode='kaa.filetype.python.pythonmode.PythonMode',
             keys = {
                    ((ctrl, 'q'), '2'):
                        'editor.splithorz'})   # Assign C-q 2 to split window.
    """

    add_class_addon(filemode, 'keybind', (editmode, keymap))


def command(commandid,
            filemode='kaa.filetype.default.defaultmode.DefaultMode'):
    """Decorator to register command.

    commandid -- command id
    filemode -- Mode class name to register keybind.
                  (default 'kaa.filetype.default.defaultmode.DefaultMode)

    ex)
        @command(filemode='kaa.filetype.python.pythonmode.PythonMode',
                 commandid='abc.def')
        @norec
        def abc_def(wnd):
            pass
    """

    def _f(f):
        kaa.command.commandid(commandid)(f)
        add_class_addon(filemode, 'command', f)
        return f
    return _f


# theme_def(filetype='kaa.filetype.python', theme={
#   'basic': [
#    	Sytle('default', 'white', 'black'),
#   ])

def theme_def(filemode='kaa.filetype.default.defaultmode.DefaultMode',
              theme=None):
    """Update theme color.

    filemode -- Mode class name to register keybind.
                  (default 'kaa.filetype.default.defaultmode.DefaultMode)
    theme -- Dictionary of theme name and list of styles. Currently, the only
             valid theme name is 'basic'.

    ex)
        # update default foreground color to red.
        theme_def(theme={
            'basic': [
               Style('default', 'red', None),
            ]})

    """

    add_class_addon(filemode, 'style', theme)


# add_filetype('my.python.filetype')

def add_filetype(name):
    """Register filetype package.

    name -- name of filetype package in string.
    """

    kaa.config.FILETYPES.append(name)
