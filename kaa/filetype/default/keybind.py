from kaa.keyboard import *

# application commands
app_keys = {
    (alt, '/'): 'app.mainmenu',
    f1: 'app.mainmenu',
}

# default cursor commands
cursor_keys = {
    left: ('screen.selection.clear', 'cursor.left'),
    right:('screen.selection.clear', 'cursor.right'),
    up: ('screen.selection.clear', 'cursor.up'),
    down: ('screen.selection.clear', 'cursor.down'),

    (ctrl, left): ('screen.selection.clear', 'cursor.word-left'),
    (ctrl, right):('screen.selection.clear', 'cursor.word-right'),

    pagedown:('screen.selection.clear', 'cursor.pagedown'),
    pageup:('screen.selection.clear', 'cursor.pageup'),

    (shift, left): ('screen.selection.begin', 'cursor.left', 'screen.selection.set_end'),
    (shift, right): ('screen.selection.begin', 'cursor.right', 'screen.selection.set_end'),
    (shift, up): ('screen.selection.begin', 'cursor.up', 'screen.selection.set_end'),
    (shift, down): ('screen.selection.begin', 'cursor.down', 'screen.selection.set_end'),

    (shift, ctrl, left): ('screen.selection.begin', 'cursor.word-left', 'screen.selection.set_end'),
    (shift, ctrl, right):('screen.selection.begin', 'cursor.word-right', 'screen.selection.set_end'),

    (alt, left): ('screen.selection.clear', 'cursor.word-left'),
    (alt, right): ('screen.selection.clear', 'cursor.word-right'),
}


# edit commands
edit_command_keys = {
    backspace: 'edit.backspace',
    delete: 'edit.delete',
    (ctrl, 'z'): 'edit.undo',
    (ctrl, 'r'): 'edit.redo',
}

# macro commands
macro_command_keys = {
    f6: 'macro.toggle-record',
    f5: 'macro.run',
}

# search commands
search_command_keys = {
    (ctrl, 's'): 'search.showsearch',
    (alt, 's'): 'search.showreplace',
}

# emacs like keys
emacs_keys = {
    (ctrl, 'b'): cursor_keys[left],
    (ctrl, 'f'): cursor_keys[right],
    (ctrl, 'p'): cursor_keys[up],
    (ctrl, 'n'): cursor_keys[down],

    (alt, 'b'): ('screen.selection.clear', 'cursor.word-left'),
    (alt, 'f'): ('screen.selection.clear', 'cursor.word-right'),
    (alt, 'B'): ('screen.selection.begin', 'cursor.word-left', 'screen.selection.set_end'),
    (alt, 'F'): ('screen.selection.begin', 'cursor.word-right', 'screen.selection.set_end'),

    (ctrl, 'v'): cursor_keys[pagedown],
    (alt, 'v'): cursor_keys[pageup],

    (alt, '<'): 'cursor.top-of-file',
    (alt, '>'): 'cursor.end-of-file',
}


# vi like commands
normal_mode_keys = {
    # normal mode
    'h': 'cursor.left',
    'l': 'cursor.right',
    'k': 'cursor.up',
    'j': 'cursor.down',
    'gg': 'cursor.top-of-file',
    'G': 'cursor.top-of-file',

    # edit
    'x': 'edit.delete',

    # mode change
    'i': 'mode.insert',
    'v': 'mode.visual',
    'V': 'mode.visual-linewise',

    # undo/redo
    'u': 'edit.undo',
    (ctrl, 'r'): 'edit.redo',
}

visual_mode_keys = {
    left: ('screen.selection.begin', 'cursor.left', 'screen.selection.set_end'),
    right: ('screen.selection.begin', 'cursor.right', 'screen.selection.set_end'),
    up: ('screen.selection.begin', 'cursor.up', 'screen.selection.set_end'),
    down: ('screen.selection.begin', 'cursor.down', 'screen.selection.set_end'),

    pagedown:('screen.selection.begin', 'cursor.pagedown', 'screen.selection.set_end'),
    pageup:('screen.selection.begin', 'cursor.pageup', 'screen.selection.set_end'),

    'h': ('screen.selection.begin', 'cursor.left', 'screen.selection.set_end'),
    'l': ('screen.selection.begin', 'cursor.right', 'screen.selection.set_end'),
    'k': ('screen.selection.begin', 'cursor.up', 'screen.selection.set_end'),
    'j': ('screen.selection.begin', 'cursor.down', 'screen.selection.set_end'),

    'gg': ('screen.selection.begin', 'cursor.top-of-file', 'screen.selection.set_end'),
    'G': ('screen.selection.begin', 'cursor.top-of-file', 'screen.selection.set_end'),

}

visual_linewise_mode_keys = {
    left: ('screen.lineselection.begin', 'cursor.left', 'screen.lineselection.set_end'),
    right: ('screen.lineselection.begin', 'cursor.right', 'screen.lineselection.set_end'),
    up: ('screen.lineselection.begin', 'cursor.up', 'screen.lineselection.set_end'),
    down: ('screen.lineselection.begin', 'cursor.down', 'screen.lineselection.set_end'),

    pagedown:('screen.lineselection.begin', 'cursor.pagedown', 'screen.lineselection.set_end'),
    pageup:('screen.lineselection.begin', 'cursor.pageup', 'screen.lineselection.set_end'),

    'h': ('screen.lineselection.begin', 'cursor.left', 'screen.lineselection.set_end'),
    'l': ('screen.lineselection.begin', 'cursor.right', 'screen.lineselection.set_end'),
    'k': ('screen.lineselection.begin', 'cursor.up', 'screen.lineselection.set_end'),
    'j': ('screen.lineselection.begin', 'cursor.down', 'screen.lineselection.set_end'),

    'gg': ('screen.lineselection.begin', 'cursor.top-of-file', 'screen.lineselection.set_end'),
    'G': ('screen.lineselection.begin', 'cursor.top-of-file', 'screen.lineselection.set_end'),

}
