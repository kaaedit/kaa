import curses
import os
import fnmatch
import re

import kaa
from kaa import document
from kaa.theme import Style
from kaa.ui.filenameindex import filenameindexmode

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
    res = [fnmatch.translate(name) for name in filenames.split(' ')]
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


def _enc_japanese(filename):
    encoding = kaa.app.storage.guess_japanese_encoding(filename)
    if encoding:
        return encoding
    else:
        kaa.app.messagebar.set_message(
            'Cannot detect text encoding:: {}'.format(filename))


def _grep(filename, regex, encoding, newline):
    doc = document.Document.find_filename(filename)
    if doc:
        text = doc.gettext(0, doc.endpos())
    else:
        if encoding == 'japanese':
            encoding = _enc_japanese(filename)

        fileinfo = kaa.app.storage.get_fileinfo(filename, encoding=encoding,
                                                newline=newline)
        f = kaa.app.storage.get_textio(fileinfo)
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


def _search(dir, option, doc):
    mode = doc.mode
    style_default = mode.get_styleid('default')
    style_filename = mode.get_styleid('filenameindex-filename')
    style_lineno = mode.get_styleid('filenameindex-lineno')
    style_match = mode.get_styleid('grep-match')

    def add_hit():
        doc.append(path, style_filename)
        doc.append(':', style_filename)
        doc.append(str(cur_lineno), style_lineno)
        doc.append(':', style_lineno)
        doc.append(' ', style_default)

        linefrom, lineto = linerange
        pos = f = t = 0
        for f, t in matches:
            f -= linefrom
            t -= linefrom
            if f != pos:
                doc.append(cur_line[pos:f], style_default)

            doc.append(cur_line[f:t], style_match)
            pos = t

        if pos != len(cur_line):
            doc.append(cur_line[t:], style_default)

        doc.append('\n', style_default)

    files = _walk(dir, option.filenames, option.tree)
    regex = option.get_regex()

    nfiles = 0
    nhits = 0

    # todo: use raw mode to accept ^C
    for fname in files:
        print(fname)

        nfiles += 1

        cur_lineno = None
        matches = []

        path = kaa.utils.shorten_filename(fname)
        if len(path) > len(fname):
            path = fname

        for rec in _grep(fname, regex, option.encoding, option.newline):
            lineno, linefrom, lineto, line, f, t, match = rec
            nhits += 1

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
    return nfiles, nhits


def grep(option, target):

# todo: reuse grep pane in same frame
#        buddy = wnd.splitter.get_buddy()
#        if not buddy:
#            buddy = wnd.splitter.split(vert=False, doc=doc)
#            self._locate_doc(buddy.wnd, doc, lineno)
#        else:
#            if buddy.wnd and buddy.wnd.document is doc:
#                self._locate_doc(buddy.wnd, doc, lineno)
#                return
#

    if not target:
        doc = document.Document()
        mode = GrepMode()
        doc.setmode(mode)
    else:
        doc = target.document
        doc.delete(0, doc.endpos())
        mode = doc.mode

    doc.set_title('<grep>')
    mode.grepoption = option.clone()
    mode.encoding = mode.grepoption.encoding
    mode.newlilne = mode.grepoption.newline

    dir = os.path.abspath(os.path.expanduser(option.directory))
    if not os.path.isdir(dir):
        s = 'Cannot find directory `{}`.'.format(dir)
        doc.append(s)
    else:
        try:
            # Restore to cooked mode to accept ^C.
            curses.def_prog_mode()
            curses.endwin()

            try:
                print('Hit ^C to cancel grep.')
                nfiles, nhits = _search(dir, option, doc)
            finally:
                curses.reset_prog_mode()
                kaa.app.mainframe.refresh()

        except KeyboardInterrupt:
            kaa.app.messagebar.set_message('Grep canceled')
            return

        if not nfiles:
            s = 'Cannot find file `{}`.'.format(option.filenames)
            doc.append(s)
        elif not nhits:
            s = 'Cannot find `{}`.'.format(option.text)
            doc.append(s)
        else:
            s = 'Found {} times in {} files'.format(nhits, nfiles)

    kaa.app.messagebar.set_message(s)

    if not target:
        kaa.app.show_doc(doc)
    else:
        target.activate()


GrepThemes = {
    'basic': [
        Style('grep-match', 'Orange', None),
    ],
}


class GrepMode(filenameindexmode.FilenameIndexMode):
    MODENAME = 'Grep'

    def init_themes(self):
        super().init_themes()
        self.themes.append(GrepThemes)
