from kaa.keyboard import *

# application commands
app_keys = {
    (alt, '/'): 'app.mainmenu',
    f1: 'app.mainmenu',
    f9: 'app.global.prev',
    f10: 'app.global.next',
    (alt, 'w'): 'menu.window',
}

# default cursor commands
cursor_keys = {
    left: 'cursor.left',
    right: 'cursor.right',
    up: 'cursor.up',
    down: 'cursor.down',

    (ctrl, left): 'cursor.word-left',
    (ctrl, right): 'cursor.word-right',

    pagedown: 'cursor.pagedown',
    pageup: 'cursor.pageup',

    (shift, left): 'cursor.left.select',
    (shift, right): 'cursor.right.select',
    (shift, up): 'cursor.up.select',
    (shift, down): 'cursor.down.select',

    (shift, ctrl, left): 'cursor.word-left.select',
    (shift, ctrl, right): 'cursor.word-right.select',

    home: ('cursor.home'),
    end: ('cursor.end'),

    (shift, home): 'cursor.home.select',
    (shift, end): 'cursor.end.select',

    (ctrl, home): 'cursor.top-of-file',
    (ctrl, end): 'cursor.end-of-file',

    (shift, ctrl, home): 'cursor.top-of-file.select',
    (shift, ctrl, end): 'cursor.end-of-file.select',

    (alt, 'a'): 'selection.all',

    (alt, 'c'): 'selection.expand-sel',

    (ctrl, '@'): 'selection.set-mark',
    (alt, '#'): 'selection.set-rectangle-mark',
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

    (ctrl, 'x'): 'edit.cut',
    (ctrl, 'c'): 'edit.copy',
    (ctrl, 'v'): 'edit.paste',
    (ctrl, 'z'): 'edit.undo',
    (ctrl, 'y'): 'edit.redo',

    (alt, 'v'): 'edit.clipboard-history',
}

addtional_edit_command_keys = {
    (ctrl, 'g'): 'cursor.go-to-line',

    tab: 'edit.indent',
    (shift, tab): 'edit.dedent',

    ((alt, 'm'), (alt, 'v')): 'menu.edit.convert',
    ((ctrl, 'u'), (alt, '!')): 'tools.execute-shell-command',

    (ctrl, 'o'): 'edit.word-complete',
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
    (ctrl, 'b'): 'cursor.left',
    (ctrl, 'f'): 'cursor.right',
    (ctrl, 'p'): 'cursor.prev-line',
    (ctrl, 'n'): 'cursor.next-line',

    (alt, 'b'): 'cursor.word-left',
    (alt, 'f'): 'cursor.word-right',

    (ctrl, 'a'): 'cursor.top-of-line',
    (ctrl, 'e'): 'cursor.end-of-line',

    (alt, 'n'): 'cursor.pagedown',
    (alt, 'p'): 'cursor.pageup',

    (alt, '<'): 'cursor.top-of-file',
    (alt, '>'): 'cursor.end-of-file',
}


# vi like commands
command_mode_keys = {
    # command mode
    'h': 'cursor.left',
    'l': 'cursor.right',
    'k': 'cursor.up',
    'j': 'cursor.down',
    'gg': 'cursor.top-of-file',
    'G': 'cursor.end-of-file',

    # edit
    'x': 'edit.delete',

    # editmode change
    'i': 'editmode.insert',
    'v': ('editmode.visual', 'selection.set-mark'),
    #    'V': ('editmode.visual-linewise', 'cursor.home', 'selection.set-mark'),

    # undo/redo
    'u': 'edit.undo',
    (ctrl, 'r'): 'edit.redo',
}

visual_mode_keys = {
    left: 'cursor.left',
    right: 'cursor.right',
    up: 'cursor.up',
    down: 'cursor.down',

    pagedown: 'cursor.pagedown',
    pageup: 'cursor.pageup',

    'h': 'cursor.left',
    'l': 'cursor.right',
    'k': 'cursor.up',
    'j': 'cursor.down',

    'gg': 'cursor.top-of-file',
    'G': 'cursor.end-of-file',

    'y': ('edit.copy', 'selection.end-cursor', 'editmode.command'),
}

visual_linewise_mode_keys = {
    up: ('cursor.up', 'cursor.end'),
    down: ('cursor.down', 'cursor.end'),

    'k': ('cursor.up', 'cursor.end'),
    'j': ('cursor.down', 'cursor.end'),

    'y': ('edit.copy', 'selection.end-cursor', 'editmode.command'),
}
