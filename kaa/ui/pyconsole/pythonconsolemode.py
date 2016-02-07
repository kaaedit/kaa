import curses
import code
import sys
import time
from contextlib import contextmanager
import kaa
from kaa import document
from kaa.keyboard import *
from kaa.filetype.python import pythonmode
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa.theme import Style

pythonconsole_keys = {
    ('\r'): 'pythonconsole.newline',
    (alt, '\r'): 'pythonconsole.script-history',
    (alt, '\n'): 'pythonconsole.script-history',
}

PythonConsoleThemes = {
    'basic': [
        Style('stdout', 'Orange', 'Default'),
        Style('stderr', 'Magenta', 'Default'),
        Style('ps', 'Blue', 'Default'),
    ],
}


class KaaInterpreter(code.InteractiveInterpreter):
    localdict = {"__name__": "__console__", "__doc__": None}

    def __init__(self, document):
        super().__init__(self.localdict)
        self.document = document

    def runcode(self, code):
        # stop undo
        self.document.use_undo(False)
        # send newline before running script
        sys.stdout.write('\n')
        try:
            super().runcode(code)
        finally:
            # stop undo
            self.document.use_undo(True)

    def showsyntaxerror(self, filename=None):
        # stop undo
        self.document.use_undo(False)
        # send newline before show error
        sys.stdout.write('\n')
        try:
            super().showsyntaxerror(filename)
        finally:
            # stop undo
            self.document.use_undo(True)


class PythonConsoleMode(pythonmode.PythonMode):
    DEFAULT_STATUS_MSG = 'Hit alt+Enter for history.'
    MODENAME = 'Python console'
    DOCUMENT_MODE = False
    SHOW_BLANK_LINE = False

    PYTHONCONSOLE_KEY_BINDS = [
        pythonconsole_keys,
    ]

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.PYTHONCONSOLE_KEY_BINDS)

    def init_themes(self):
        super().init_themes()
        self.themes.append(PythonConsoleThemes)

    def on_set_document(self, document):
        super().on_set_document(document)
        self.interp = KaaInterpreter(document=document)

        self.document.append(
            'Python %s\n' %
            sys.version, self.get_styleid('ps'))
        self.document.append('>>>', self.get_styleid('ps'))
        self.document.append('\n', self.get_styleid('default'))
        p = self.document.endpos()
        self.document.marks['current_script'] = (p, p)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        f, t = self.document.marks['current_script']
        wnd.cursor.setpos(f)

    def _get_highlight_range(self):
        return self.document.marks['current_script']

    @commandid('pythonconsole.clear')
    @norec
    @norerun
    def clear_line(self, wnd):
        f, t = self.document.marks['current_script']
        self.document.delete(f, t)
        wnd.cursor.setpos(f)
        self.document.undo.clear()

    def on_esc_pressed(self, wnd, event):
        self.clear_line(wnd)

    def put_string(self, wnd, s, overwrite=False):
        pos = wnd.cursor.pos
        f, t = self.document.marks['current_script']
        if not (f <= pos <= t):
            wnd.cursor.setpos(t)
            wnd.screen.selection.clear()

        super().put_string(wnd, s, overwrite)

    def replace_string(self, wnd, pos, posto, s, update_cursor=True):
        f, t = self.document.marks['current_script']
        if not (f <= pos <= t):
            return
        if not (f <= posto <= t):
            return

        super().replace_string(wnd, pos, posto, s, update_cursor)

    def delete_string(self, wnd, pos, posto, update_cursor=True):
        f, t = self.document.marks['current_script']
        if not (f <= pos <= t):
            return
        if not (f <= posto <= t):
            return

        super().delete_string(wnd, pos, posto, update_cursor)

    @contextmanager
    def _redirect_output(self, wnd):
        stdin = sys.stdin
        stdout = sys.stdout
        stderr = sys.stderr

        style_stdout = self.get_styleid('stdout')
        style_stderr = self.get_styleid('stderr')

        class out:

            def __init__(self, document, style):
                self.document = document
                self.style = style
                self._cache = []

            def write(self, s):
                if self.document.closed:
                    return
                self._cache.append(s)
                if '\n' in s:
                    self.flush()

            def flush(self):
                if self._cache:
                    self.document.append(''.join(self._cache), self.style)
                    self._cache = []

        sys.stdin = None
        sys.stdout = out(self.document, style_stdout)
        sys.stderr = out(self.document, style_stderr)

        try:
            yield

        finally:
            sys.stdout.flush()
            sys.stderr.flush()

            sys.stdin = stdin
            sys.stdout = stdout
            sys.stderr = stderr

    @commandid('pythonconsole.exec')
    @norec
    @norerun
    def exec_script(self, wnd):
        f, t = self.document.marks['current_script']
        s = wnd.document.gettext(f, t).lstrip().rstrip(' \t')
        with self._redirect_output(wnd):
            curses.cbreak()
            try:
                start = time.time()
                ret = self.interp.runsource(s)
                end = time.time()
            finally:
                curses.raw()

            if not ret:
                kaa.app.messagebar.set_message(
                    'Execued in {} secs'.format(end - start))
                wnd.document.undo.clear()
                if s.strip():
                    hist = kaa.app.config.hist(
                        'pyconsole_script',
                        self.MAX_HISTORY)
                    hist.add(s)

                self.document.append('>>>', self.get_styleid('ps'))
                self.document.append('\n', self.get_styleid('default'))
                p = self.document.endpos()
                self.document.marks['current_script'] = (p, p)
                wnd.cursor.setpos(p)
            else:
                self.on_commands(wnd, ['edit.newline'])
                return

    @commandid('pythonconsole.newline')
    def on_enter(self, wnd):
        f, t = self.document.marks['current_script']

        if wnd.cursor.pos < f:
            wnd.cursor.setpos(f)
            return

        tail = wnd.document.gettext(wnd.cursor.pos, t).strip()
        if tail:
            self.on_commands(wnd, ['edit.newline'])
            return

        self.exec_script(wnd)

    def _put_script(self, wnd, text):
        if text.endswith('\n'):
            text = text[:-1]

        self.put_string(wnd, text)
        wnd.screen.selection.clear()
        hist = kaa.app.config.hist('pyconsole_script', self.MAX_HISTORY)
        hist.add(text)

    MAX_HISTORY = 100

    @commandid('pythonconsole.script-history')
    @norec
    @norerun
    def history(self, wnd):
        hist = kaa.app.config.hist('pyconsole_script', self.MAX_HISTORY)
        scripts = [p for p, i in hist.get()]
        if not scripts:
            return

        def callback(text):
            if text:
                self._put_script(wnd, text)

        from kaa.ui.texthist import texthistmode
        texthistmode.show_history('Search history:', callback, scripts)

    @commandid('edit.paste')
    def paste(self, wnd):
        s = kaa.app.clipboard.get()
        if s:
            self._put_script(wnd, s)


def show_console():
    cons = document.Document()
    mode = PythonConsoleMode()
    cons.setmode(mode)
    cons.set_title('<Python console>')

    kaa.app.show_doc(cons)
    kaa.app.messagebar.set_message('')
