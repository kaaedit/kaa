from kaa.keyboard import *

# application commands
app_keys = {
    (alt, '/'): 'app.mainmenu',
    f1: 'app.mainmenu',
    f9: 'app.global.prev',
    f10: 'app.global.next',
}

# default cursor commands
cursor_keys = {
    left: ('selection.end-cursor', 'cursor.left', 'selection.set-to'),
    right:('selection.end-cursor', 'cursor.right', 'selection.set-to'),
    up: ('selection.end-cursor', 'cursor.up', 'selection.set-to'),
    down: ('selection.end-cursor', 'cursor.down', 'selection.set-to'),

    (ctrl, left): ('selection.end-cursor', 'cursor.word-left', 'selection.set-to'),
    (ctrl, right):('selection.end-cursor', 'cursor.word-right', 'selection.set-to'),

    pagedown:('selection.end-cursor', 'cursor.pagedown', 'selection.set-to'),
    pageup:('selection.end-cursor', 'cursor.pageup', 'selection.set-to'),

    (shift, left): ('selection.begin-cursor', 'cursor.left', 'selection.set-to'),
    (shift, right): ('selection.begin-cursor', 'cursor.right', 'selection.set-to'),
    (shift, up): ('selection.begin-cursor', 'cursor.up', 'selection.set-to'),
    (shift, down): ('selection.begin-cursor', 'cursor.down', 'selection.set-to'),

    (shift, ctrl, left): ('selection.begin-cursor', 'cursor.word-left', 'selection.set-to'),
    (shift, ctrl, right):('selection.begin-cursor', 'cursor.word-right', 'selection.set-to'),

    home: ('selection.end-cursor', 'cursor.home', 'selection.set-to'),
    end: ('selection.end-cursor', 'cursor.end', 'selection.set-to'),

    (shift, home): ('selection.begin-cursor', 'cursor.home', 'selection.set-to'),
    (shift, end): ('selection.begin-cursor', 'cursor.end', 'selection.set-to'),

    (ctrl, home): ('selection.end-cursor', 'cursor.top-of-file', 'selection.set-to'),
    (ctrl, end): ('selection.end-cursor', 'cursor.end-of-file', 'selection.set-to'),

    (shift, ctrl, home): ('selection.begin-cursor', 'cursor.top-of-file', 'selection.set-to'),
    (shift, ctrl, end): ('selection.begin-cursor', 'cursor.end-of-file', 'selection.set-to'),

    (alt, 'a'): 'screen.selection.all',

    (ctrl, 'c'): 'screen.selection.expand_sel',

    (ctrl, '@'): 'screen.selection.setmark',
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
    (ctrl, 'u'): 'edit.undo',
    (alt, 'u'): 'edit.redo',

}

addtional_edit_command_keys = {
    (ctrl, 'g'): ('selection.end-cursor', 'cursor.go-to-line', 'selection.set-to'),

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
    f2: 'search.prev',
    f3: 'search.next',
}

# emacs like keys
emacs_keys = {
    (ctrl, 'b'): ('cursor.left', 'selection.set-to'),
    (ctrl, 'f'): ('cursor.right', 'selection.set-to'),
    (ctrl, 'p'): ('cursor.up', 'selection.set-to'),
    (ctrl, 'n'): ('cursor.down', 'selection.set-to'),

    (alt, 'b'): ('cursor.word-left', 'selection.set-to'),
    (alt, 'f'): ('cursor.word-right', 'selection.set-to'),

    (ctrl, 'a'): ('cursor.home'),
    (ctrl, 'e'): ('cursor.end'),

    (ctrl, 'v'): ('cursor.pagedown', 'selection.set-to'),
    (alt, 'v'): ('cursor.pageup', 'selection.set-to'),

    (alt, '<'): ('cursor.top-of-file', 'selection.set-to'),
    (alt, '>'): ('cursor.end-of-file', 'selection.set-to'),
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
    left: ('selection.begin-cursor', 'cursor.left', 'selection.set-to'),
    right: ('selection.begin-cursor', 'cursor.right', 'selection.set-to'),
    up: ('selection.begin-cursor', 'cursor.up', 'selection.set-to'),
    down: ('selection.begin-cursor', 'cursor.down', 'selection.set-to'),

    pagedown:('selection.begin-cursor', 'cursor.pagedown', 'selection.set-to'),
    pageup:('selection.begin-cursor', 'cursor.pageup', 'selection.set-to'),

    'h': ('selection.begin-cursor', 'cursor.left', 'selection.set-to'),
    'l': ('selection.begin-cursor', 'cursor.right', 'selection.set-to'),
    'k': ('selection.begin-cursor', 'cursor.up', 'selection.set-to'),
    'j': ('selection.begin-cursor', 'cursor.down', 'selection.set-to'),

    'gg': ('selection.begin-cursor', 'cursor.top-of-file', 'selection.set-to'),
    'G': ('selection.begin-cursor', 'cursor.end-of-file', 'selection.set-to'),

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

