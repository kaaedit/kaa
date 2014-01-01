from kaa.keyboard import *

_class_addoons = {}

def add_class_addon(classname, key, value):
    d = _class_addoons.setdefault(classname, {})
    d.setdefault(key, []).append(value)

def get_addon(name, key):
    d = _class_addoons.get(name, None)
    if d:
        return d.get(key, ())
    return () 

# keybind(filetype='kaa.filetype.python', editmode='input', {
# })

def keybind(filetype=None, editmode='input', keymap=None):
    pass


# @command(filetype='kaa.filetype.python.pythonmode.PythonMode', 
#          commandid='abc.def')
# @norec
# def abc_def(wnd):
#    pass

def command(commandid, filetype=None):
    pass


#style_def(filetype='kaa.filetype.python', theme='basic', [
#    Sytle('default', 'white', 'black'),
#])

def style_def(filetype, theme, styles):
    pass

# add_filetype('my.python.filetype',
#    overrides='kaa.filetype.python')

