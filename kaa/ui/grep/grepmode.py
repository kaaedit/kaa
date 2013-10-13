import os
import fnmatch
import re

import kaa
from kaa import document
from kaa.keyboard import *
from kaa.theme import Theme, Style
from kaa.filetype.default import modebase, keybind, defaultmode
from kaa.ui.msgbox import msgboxmode
from kaa.command import command, Commands, norec, norerun
from kaa.commands import editorcommand

FILES_IGNORE = [
'*.com',
'*.class',
'*.dll',
'*.exe',
'*.o',
'*.a',
'*.so',
'*.pyc',
'*.pyo',

'*.7z',
'*.dmg',
'*.gz',
'*.bz2',
'*.iso',
'*.jar',
'*.rar',
'*.tar',
'*.zip',

'*.png',
'*.gif',
'*.jpeg',
'*.jpg',
'*.bmp',

'.DS_Store',
'.Trashes',
'ehthumbs.db',
'Thumbs.db',

'*.bak',
'#*#',
'*.swp',
]

DIRS_IGNORE = [
'.git',
'.hg',
'.bzr',
'.svn',
'CVS',
'__pycache__',
]


def _build_fnre(filenames):
    res = [fnmatch.translate(name) for name in filenames.split(':')]
    return re.compile('|'.join(res))
    
def _walk(dirname, filenames, tree):
    fn = _build_fnre(filenames)

    ignores = [fnmatch.translate(name) for name in FILES_IGNORE]
    fn_ignore = re.compile('|'.join(ignores))
    
    ignores = [fnmatch.translate(name) for name in DIRS_IGNORE]
    dir_ignore = re.compile('|'.join(ignores))
    
    for root, dirs, files in os.walk(dirname, topdown=True):
        files = [os.path.join(root, name) for name in files 
                    if fn.match(name) and not fn_ignore.match(name)]
        yield from files
        if not tree:
            return

        dirs[:] = [dir for dir in dirs if not dir_ignore.match(dir)]

def _iter_lines(text):
    lineno = 1
    pos = 0
    while True:
        next = text.find('\n', pos)
        if next == -1:
            break
        next = next + 1
        yield lineno, pos, next, text[pos:next]
        lineno += 1
        pos = next
    
    yield lineno, pos, len(text), text[pos:]
    
def _grep(filename, regex):
    f, fileinfo = kaa.app.storage.get_textio(filename, 'r')
    if not f:
        return
    with f:
        text = f.read()

    lines = _iter_lines(text)
    lineno, linefrom, lineto, line = next(lines)
    
    for m in regex.finditer(text):
        f, t = m.span()
        while f >= lineto:
            lineno, linefrom, lineto, line = next(lines)

        yield lineno, linefrom, lineto, line, f, t, text[f:t]


def grep(config):
    dir = os.path.abspath(os.path.expanduser(config.directory))
    files = _walk(dir, config.filenames, config.tree)
    regex = config.get_regex()
    

    buf = document.Buffer()
    doc = document.Document(buf)
    mode = GrepMode()
    doc.setmode(mode)

    style_default = mode.get_styleid('default')
    style_filename = mode.get_styleid('grep-filename')
    style_lineno = mode.get_styleid('grep-lineno')
    style_match = mode.get_styleid('grep-match')
    
    def add_hit():
        doc.append(path, style_filename)
        doc.append(':', style_default)
        doc.append(str(cur_lineno), style_lineno)
        doc.append(': ', style_default)
        
        linefrom, lineto = linerange
        pos = f = t = 0
        for f, t in matches:
            f -= linefrom
            t -= linefrom
            if f != pos:
                doc.append(cur_line[pos:f], style_default)

            doc.append(cur_line[f:t], style_match)
            pos = t
            
        if pos != len(line):
            doc.append(cur_line[t:], style_default)

        doc.append('\n', style_default)
        
    # todo: use raw mode to accept ^C
    for fname in files:
        cur_lineno = None
        matches = []
        
        path = os.path.relpath(fname)
        if len(path) > len(fname):
            path = fname
            
        for lineno, linefrom, lineto, line, f, t, match in _grep(fname, regex):
            line = line.rstrip('\n')
            if cur_lineno is None:
                cur_lineno = lineno
                linerange = linefrom, lineto
                cur_line = line
                
            if matches and (lineno != cur_lineno):
                add_hit()
                matches = []
                linerange = linefrom, lineto
                cur_lineno = lineno
                cur_line = line
            
            matches.append((f, t))
        
        if matches:
            add_hit()
    
    kaa.app.show_doc(doc)
    
    
GrepThemes = {
    'default':
        Theme([
            Style('grep-filename', 'blue', 'default', bold=True),
            Style('grep-lineno', 'Magenta', 'default'),
            Style('grep-match', 'Red', 'default'),
        ])
}


grep_keys = {
    '\r': ('grepdlg.field.next'),
    '\n': ('grepdlg.field.next'),
}



class GrepMode(defaultmode.DefaultMode):
    MODENAME = 'Grep'
    USE_UNDO = False

    GREP_KEY_BINDS = [
        grep_keys,
    ]

    def init_themes(self):
        super().init_themes()
        self.themes.append(GrepThemes)

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.GREP_KEY_BINDS)

    def init_tokenizers(self):
        self.tokenizers = []
