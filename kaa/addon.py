from kaa.keyboard import *
from kaa.theme import Style
import kaa.command
from kaa.command import norec, norerun, commandid
import kaa.config
_class_addons = {}


def add_class_addon(classname, key, value):
    d = _class_addons.setdefault(classname, {})
    d.setdefault(key, []).append(value)


def get_addon(name, key, default=()):
    d = _class_addons.get(name, None)
    if d:
        return d.get(key, default)
    return default

# keybind(
#     filemode='kaa.filetype.python.pythonmode.PythonMode', 
#     editmode='input', 
#     keys = {
#     })


def keybind(filemode='kaa.filetype.default.defaultmode.DefaultMode',
            editmode='input', keymap=None):
    
    add_class_addon(filemode, 'keybind', (editmode, keymap))	

# @command(filemode='kaa.filetype.python.pythonmode.PythonMode',
#          commandid='abc.def')
# @norec
# def abc_def(wnd):
#    pass

def command(commandid, 
        filemode='kaa.filetype.default.defaultmode.DefaultMode'):

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
    add_class_addon(filemode, 'style', theme)


# add_filetype('my.python.filetype')

def add_filetype(name):
    kaa.config.FILETYPES.append(name)
