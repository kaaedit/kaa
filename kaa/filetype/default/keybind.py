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

    (shift, left): ('screen.selection.begin', 'cursor.left', 'screen.selection.set-end'),
    (shift, right): ('screen.selection.begin', 'cursor.right', 'screen.selection.set-end'),
    (shift, up): ('screen.selection.begin', 'cursor.up', 'screen.selection.set-end'),
    (shift, down): ('screen.selection.begin', 'cursor.down', 'screen.selection.set-end'),

    (shift, ctrl, left): ('screen.selection.begin', 'cursor.word-left', 'screen.selection.set-end'),
    (shift, ctrl, right):('screen.selection.begin', 'cursor.word-right', 'screen.selection.set-end'),

    home: ('screen.selection.clear', 'cursor.home'),
    end: ('screen.selection.clear', 'cursor.end'),

    (shift, home): ('screen.selection.begin', 'cursor.home', 'screen.selection.set-end'),
    (shift, end): ('screen.selection.begin', 'cursor.end', 'screen.selection.set-end'),

    (ctrl, home): ('screen.selection.clear', 'cursor.top-of-file'),
    (ctrl, end): ('screen.selection.clear', 'cursor.end-of-file'),

    (shift, ctrl, home): ('screen.selection.begin', 'cursor.top-of-file', 'screen.selection.set-end'),
    (shift, ctrl, end): ('screen.selection.begin', 'cursor.end-of-file', 'screen.selection.set-end'),

    (ctrl, 'g'): ('screen.selection.clear', 'cursor.go-to-line'),

    (alt, 'a'): 'screen.selection.all',

    (ctrl, 'c'): 'screen.selection.expand_sel',
}


# edit commands
edit_command_keys = {
    backspace: 'edit.backspace',
    (ctrl, 'h'): 'edit.backspace',
    (alt, 'h'): 'edit.backspace.word',

    delete: 'edit.delete',
    (ctrl, 'd'): 'edit.delete',
    (alt, 'd'): 'edit.delete.word',

    (ctrl, 'k'): 'edit.delete.line',
    (alt, 'k'): 'edit.delete.currentline',

    '\r': 'edit.newline',
    '\n': 'edit.newline',

    (ctrl, 'w'): 'edit.cut',
    (alt, 'w'): 'edit.copy',
    (ctrl, 'y'): 'edit.paste',
    (ctrl, '_'): 'edit.undo',
    (alt, '_'): 'edit.redo',

}

addtional_edit_command_keys = {
    tab: 'edit.indent',
    (shift, tab): 'edit.dedent',

    ((alt, 'm'), ('v')): 'menu.edit.convert',
    ((ctrl, 'u'), (alt, '!')): 'tools.execute-shell-command',
}

# macro commands
macro_command_keys = {
    f6: 'macro.toggle-record',
    f5: 'macro.run',
}

# rerun commands
rerun_keys = {
    (alt, '.'): 'command.rerun',
}



# search commands
search_command_keys = {
    (ctrl, 's'): 'search.showsearch',
    (alt, 's'): 'search.showreplace',
    f3: 'search.next',
    f4: 'search.prev',

}

# emacs like keys
emacs_keys = {
    (ctrl, 'b'): ('cursor.left', 'screen.selection.set-end'),
    (ctrl, 'f'): ('cursor.right', 'screen.selection.set-end'),
    (ctrl, 'p'): ('cursor.up', 'screen.selection.set-end'),
    (ctrl, 'n'): ('cursor.down', 'screen.selection.set-end'),

    (alt, 'b'): ('cursor.word-left', 'screen.selection.set-end'),
    (alt, 'f'): ('cursor.word-right', 'screen.selection.set-end'),

    (ctrl, 'a'): ('cursor.home'),
    (ctrl, 'e'): ('cursor.end'),

    (ctrl, 'v'): ('cursor.pagedown', 'screen.selection.set-end'),
    (alt, 'v'): ('cursor.pageup', 'screen.selection.set-end'),

    (alt, '<'): ('cursor.top-of-file', 'screen.selection.set-end'),
    (alt, '>'): ('cursor.end-of-file', 'screen.selection.set-end'),
}


# vi like commands
command_mode_keys = {
    # command mode
    'h': 'cursor.left',
    'l': 'cursor.right',
    'k': 'cursor.up',
    'j': 'cursor.down',
    'gg': 'cursor.top-of-file',
    'G': 'cursor.top-of-file',

    # edit
    'x': 'edit.delete',

    # editmode change
    'i': 'editmode.insert',
    'v': 'editmode.visual',
    'V': 'editmode.visual-linewise',

    # undo/redo
    'u': 'edit.undo',
    (ctrl, 'r'): 'edit.redo',
}

visual_mode_keys = {
    left: ('screen.selection.begin', 'cursor.left', 'screen.selection.set-end'),
    right: ('screen.selection.begin', 'cursor.right', 'screen.selection.set-end'),
    up: ('screen.selection.begin', 'cursor.up', 'screen.selection.set-end'),
    down: ('screen.selection.begin', 'cursor.down', 'screen.selection.set-end'),

    pagedown:('screen.selection.begin', 'cursor.pagedown', 'screen.selection.set-end'),
    pageup:('screen.selection.begin', 'cursor.pageup', 'screen.selection.set-end'),

    'h': ('screen.selection.begin', 'cursor.left', 'screen.selection.set-end'),
    'l': ('screen.selection.begin', 'cursor.right', 'screen.selection.set-end'),
    'k': ('screen.selection.begin', 'cursor.up', 'screen.selection.set-end'),
    'j': ('screen.selection.begin', 'cursor.down', 'screen.selection.set-end'),

    'gg': ('screen.selection.begin', 'cursor.top-of-file', 'screen.selection.set-end'),
    'G': ('screen.selection.begin', 'cursor.end-of-file', 'screen.selection.set-end'),

}

visual_linewise_mode_keys = {
    left: ('screen.lineselection.begin', 'cursor.left', 'screen.lineselection.set-end'),
    right: ('screen.lineselection.begin', 'cursor.right', 'screen.lineselection.set-end'),
    up: ('screen.lineselection.begin', 'cursor.up', 'screen.lineselection.set-end'),
    down: ('screen.lineselection.begin', 'cursor.down', 'screen.lineselection.set-end'),

    pagedown:('screen.lineselection.begin', 'cursor.pagedown', 'screen.lineselection.set-end'),
    pageup:('screen.lineselection.begin', 'cursor.pageup', 'screen.lineselection.set-end'),

    'h': ('screen.lineselection.begin', 'cursor.left', 'screen.lineselection.set-end'),
    'l': ('screen.lineselection.begin', 'cursor.right', 'screen.lineselection.set-end'),
    'k': ('screen.lineselection.begin', 'cursor.up', 'screen.lineselection.set-end'),
    'j': ('screen.lineselection.begin', 'cursor.down', 'screen.lineselection.set-end'),

    'gg': ('screen.lineselection.begin', 'cursor.top-of-file', 'screen.lineselection.set-end'),
    'G': ('screen.lineselection.begin', 'cursor.end-of-file', 'screen.lineselection.set-end'),

}

