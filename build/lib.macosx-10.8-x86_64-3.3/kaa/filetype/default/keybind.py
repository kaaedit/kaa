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

    # mode change
    'i': 'vimode.to_insert_mode',
    'v': 'vimode.to_visual_mode',
    'V': 'vimode.to_visual_line_mode',

    # undo/redo
    'u': 'edit.undo',
    (ctrl, 'r'): 'edit.redo',
}

