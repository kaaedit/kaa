import os
import kaa
from kaa import doc_re
from kaa import document
from kaa.keyboard import *
from kaa.theme import Style
from kaa.filetype.default import defaultmode
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun

FilenameIndexThemes = {
    'basic': [
        Style('filenameindex-filename', 'Green', 'Default'),
        Style('filenameindex-lineno', 'Green', 'Default'),
    ],
}

filenameindex_keys = {
    '\r': ('filenameindex.showmatch'),
    '\n': ('filenameindex.showmatch'),
}


def _enc_japanese(filename):
    encoding = kaa.app.storage.guess_japanese_encoding(filename)
    if encoding:
        return encoding
    else:
        kaa.app.messagebar.set_message(
            'Cannot detect text encoding:: {}'.format(filename))


class FilenameIndexMode(defaultmode.DefaultMode):
    # todo: rename key/command names
    DOCUMENT_MODE = False
    USE_UNDO = False
    HIGHLIGHT_CURSOR_ROW = True

    FILENAMEINDEX_KEY_BINDS = [
        filenameindex_keys,
    ]

    encoding = None
    newline = None

    def init_themes(self):
        super().init_themes()
        self.themes.append(FilenameIndexThemes)

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.FILENAMEINDEX_KEY_BINDS)

    def _locate_doc(self, wnd, doc, lineno):
        wnd.show_doc(doc)

        pos = doc.get_lineno_pos(lineno)
        tol = doc.gettol(pos)
        wnd.cursor.setpos(wnd.cursor.adjust_nextpos(wnd.cursor.pos, tol))
        wnd.activate()

    @commandid('filenameindex.showmatch')
    @norec
    @norerun
    def show_hit(self, wnd):
        pos = wnd.cursor.pos
        tol = self.document.gettol(pos)
        eol, line = self.document.getline(tol)

        try:
            filename, lineno, line = line.split(':', 2)
        except ValueError:
            return

        if not filename:
            return

        try:
            lineno = int(lineno)
        except ValueError:
            lineno = 1

        filename = os.path.abspath(os.path.expanduser(filename))
        doc = document.Document.find_filename(filename)
        if not doc:
            enc = self.encoding
            if not enc:
                enc = kaa.app.config.DEFAULT_ENCODING
            if enc == 'japanese':
                enc = _enc_japanese(filename)

            newline = self.newline
            if not newline:
                newline = kaa.app.config.DEFAULT_NEWLINE

            doc = kaa.app.storage.openfile(
                filename, encoding=enc, newline=newline)

        buddy = wnd.splitter.get_buddy()
        if not buddy:
            buddy = wnd.splitter.split(vert=False, doc=doc)
            self._locate_doc(buddy.wnd, doc, lineno)
        else:
            if buddy.wnd and buddy.wnd.document is doc:
                self._locate_doc(buddy.wnd, doc, lineno)
                return

            def callback(canceled):
                if not canceled:
                    buddy.show_doc(doc)
                    self._locate_doc(buddy.wnd, doc, lineno)
            kaa.app.app_commands.save_splitterdocs(wnd, buddy, callback)

    RE_FILENAME = doc_re.compile(
        r'(?P<FILENAME>^[^:\n]+)\:(?P<LINENO>\d+)\:.*$',
        doc_re.M | doc_re.X)

    def is_match(self, pos):
        m = self.RE_FILENAME.match(self.document, pos)
        return m

    def on_global_prev(self, wnd):
        if kaa.app.focus in self.document.wnds:
            if self.is_match(self.document.gettol(wnd.cursor.pos)):
                self.show_hit(kaa.app.focus)
                return True

        pos = wnd.cursor.pos

        while True:
            eol = self.document.gettol(pos)
            if eol:
                tol = self.document.gettol(eol - 1)
            else:
                eol = self.document.endpos()
                tol = self.document.gettol(eol)

            if self.is_match(tol):
                wnd.cursor.setpos(tol)
                self.show_hit(wnd)
                return True

            if tol == 0:
                wnd.cursor.setpos(tol)
                self.document.wnds[0].activate()
                return True

            pos = tol

    def on_global_next(self, wnd):
        if kaa.app.focus in self.document.wnds:
            if self.is_match(self.document.gettol(wnd.cursor.pos)):
                self.show_hit(kaa.app.focus)
                return True

        pos = wnd.cursor.pos
        while True:
            tol = self.document.geteol(pos)
            m = self.is_match(tol)
            if m:
                wnd.cursor.setpos(tol)
                self.show_hit(wnd)
                return True

            if self.document.geteol(tol) == self.document.endpos():
                wnd.cursor.setpos(0)
                self.document.wnds[0].activate()
                return True

            pos = tol
