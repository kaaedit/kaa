from kaa.keyboard import *

# Todo: Splitting key bind table does not make sense.
# Put them together.

# application commands
app_keys = {
    (alt, 'm'): 'app.mainmenu',
    (alt, '/'): 'app.mainmenu',
    f1: 'app.mainmenu',
    f9: 'app.global.prev',
    f10: 'app.global.next',
    (alt, 'w'): 'menu.window',
    (alt, 'z'): 'tools.suspend',
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
    (ctrl, '^'): 'cursor.first-letter-of-line',

    (alt, 'n'): 'cursor.pagedown',
    (alt, 'p'): 'cursor.pageup',

    (alt, '<'): 'cursor.top-of-file',
    (alt, '>'): 'cursor.end-of-file',
}


# vi like commands
command_mode_keys = {
    # editmode change
    'i': 'editmode.insert',
    'R': 'editmode.replace',
    'A': ('editmode.insert', 'cursor.end-of-line'),
    'v': ('editmode.visual', 'selection.set-mark'),
    'V': ('editmode.visual-linewise', 'selection.set-linewise-mark'),

    # cursor command
    'h': 'cursor.left',
    'l': 'cursor.right',
    'k': 'cursor.up',
    'j': 'cursor.down',

    'w': 'cursor.word-right',
    'b': 'cursor.word-left',

    '0': 'cursor.top-of-line',
    '^': 'cursor.first-letter-of-line',
    '$': 'cursor.end-of-line',

    'gg': 'cursor.top-of-file',
    'G': 'cursor.end-of-file',

    (ctrl, 'b'): 'cursor.pageup',
    (ctrl, 'f'): 'cursor.pagedown',

    # edit
    'r': 'edit.replace-next-char',
    'x': 'edit.delete',
    'd': 'edit.delete-next-move',

    # undo/redo
    'u': 'edit.undo',
    (ctrl, 'r'): 'edit.redo',

    # clipboard
    'y': ('edit.copy', 'editmode.command'),
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
    up: 'cursor.prev-line',
    down: 'cursor.next-line',

    'k': 'cursor.prev-line',
    'j': 'cursor.next-line',

    'y': ('edit.copy', 'selection.end-cursor', 'editmode.command'),
}
