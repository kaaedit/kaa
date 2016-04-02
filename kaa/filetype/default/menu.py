
MENUS = {
    'MAIN':
    [['[&File]', 'FILE', None],
     ['[&Edit]', 'EDIT', None],
     ['[&Code]', 'CODE', None],
     ['[&Macro]', 'MACRO', None],
     ['[&Tools]', 'TOOLS', None],
     ['[&Git]', 'GIT', None],
     ['[&Window]', 'WINDOW', None]],

    'FILE':
    [['&New', None, 'file.new'],
     ['&Open', None, 'file.open'],
     ['File &Info', None, 'file.info'],
     ['View &Diff', None, 'file.viewdiff'],
     ['&Save', None, 'file.save'],
     ['Save &As', None, 'file.saveas'],
     ['&Close', None, 'file.close'],
     ['Save a&ll', None, 'file.save.all'],
     ['Clos&e all', None, 'file.close.all'],
     ['[&Recently]', 'RECENTLY-USED-FILES', None],
     ['&Quit', None, 'file.quit']],

    'RECENTLY-USED-FILES':
    [['Recently used &Files', None, 'file.recently-used-files'],
     ['Recently used &Dirs', None, 'file.recently-used-directories']],

    'EDIT':
    [['&Cut', None, 'edit.cut'],
     ['C&opy', None, 'edit.copy'],
     ['&Paste', None, 'edit.paste'],
     ['Paste &History', None, 'edit.clipboard-history'],
     ['&Undo', None, 'edit.undo'],
     ['&Redo', None, 'edit.redo'],
     ['&Search', None, 'search.showsearch'],
     ['R&eplace', None, 'search.showreplace'],
     ['Co&mplete', None, 'edit.word-complete'],
     ['[&Convert]', 'EDIT-CONVERT', None]],

    'EDIT-CONVERT':
    [['&Upper', None, 'edit.conv.upper'],
     ['&Lower', None, 'edit.conv.lower'],
     ['&Normalization', None, 'edit.conv.nfkc'],
     ['&Full-width', None, 'edit.conv.full-width']],

    'MACRO':
    [['&Start Record', None, 'macro.start-record'],
     ['&End Record', None, 'macro.end-record'],
     ['&Run Macro', None, 'macro.run']],

    'TOOLS':
    [['&Grep', None, 'tools.grep'],
     ['Paste &Lines', None, 'edit.paste-lines'],
     ['&Shell command', None, 'tools.execute-shell-command'],
     ['&Make', None, 'tools.make'],
     ['Spell &Checker', None, 'tools.spellchecker'],
     ['&Python console', None, 'python.console'],
     ['Python &Debugger', None, 'python.debugger.run'],
     ['Python debugger s&erver', None, 'python.debugger.server'],
     ],

    'GIT':
    [['&Status', None, 'git.status'],
     ['&Log', None, 'git.log'],
     ],

    'WINDOW':
    [['&Frame list', None, 'app.show-framelist'],
     ['Split &vert', None, 'editor.splitvert'],
     ['Split &horz', None, 'editor.splithorz'],
     ['&Move separator', None, 'editor.moveseparator'],
     ['&Next window', None, 'editor.nextwindow'],
     ['&Prev window', None, 'editor.prevwindow'],
     ['&Join window', None, 'editor.joinwindow'],
     ['[&Switch file]', 'CHANGE-WINDOW', None]],

    'CHANGE-WINDOW':
    [['&Switch file', None, 'editor.switchfile'],
     ['&New file here', None, 'file.new-to'],
     ['&Open file here', None, 'file.open-to'],
     ['Recently used &Files', None, 'file.recently-used-files-to'],
     ['Recently used &Dirs', None, 'file.recently-used-directories-to']],
}
