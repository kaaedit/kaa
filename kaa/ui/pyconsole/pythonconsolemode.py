import curses
import code
import sys
import traceback
from contextlib import contextmanager
import kaa
from kaa import document
from kaa.keyboard import *
from kaa.filetype.default import defaultmode
from kaa.filetype.python import pythonmode
from kaa.command import commandid, Commands, norec, norerun
from kaa.theme import Theme, Style
from kaa.ui.dialog import dialogmode
from kaa.ui.inputline import inputlinemode

pythonconsole_keys = {
    ('\r'): 'python.exec',
    (alt, '\r'): 'python.script-history',
    (alt, '\n'): 'python.script-history',
}

PythonConsoleThemes = {
    'basic': [
        Style('stdout', 'Orange', 'Default'),
        Style('stderr', 'Magenta', 'Default'),
        Style('ps', 'Blue', 'Default'),
    ],
}


class KaaInterpreter(code.InteractiveInterpreter):

    def runcode(self, code):
        # send newline before running script
        sys.stdout.write('\n')
        super().runcode(code)

    def showsyntaxerror(self, filename=None):
        # send newline before show error
        sys.stdout.write('\n')
        super().showsyntaxerror(filename)


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

    def setup(self):
        super().setup()
        self.highlight.set_mark('current_script')

    def on_set_document(self, document):
        super().on_set_document(document)
        self.interp = KaaInterpreter()

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

    def on_esc_pressed(self, wnd, event):
        f, t = self.document.marks['current_script']
        self.document.delete(f, t)
        wnd.cursor.setpos(f)
        self.document.undo.clear()

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

            def write(self, s):
                if not self.document.closed:
                    self.document.append(s, self.style)

        sys.stdin = None
        sys.stdout = out(self.document, style_stdout)
        sys.stderr = out(self.document, style_stderr)

        yield

        sys.stdin = stdin
        sys.stdout = stdout
        sys.stderr = stderr

    @commandid('python.exec')
    @norec
    @norerun
    def exec_script(self, wnd):
        self.document.undo.clear()
        f, t = self.document.marks['current_script']
        s = wnd.document.gettext(f, t).lstrip()
        with self._redirect_output(wnd):
            curses.cbreak()
            try:
                ret = self.interp.runsource(s)
            finally:
                curses.raw()

            if not ret:
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
                self._show_inputline(wnd, s + '\n')

    def _show_inputline(self, wnd, s):
        doc = PythonInputlineMode.build(wnd, s)
        kaa.app.show_dialog(doc)
        kaa.app.messagebar.set_message('')

    def exec_str(self, wnd, s):
        s = s.rstrip() + '\n'
        f, t = self.document.marks['current_script']
        self.document.replace(f, t, s,
                              style=self.get_styleid('default'))
        self.exec_script(wnd)

    def _put_script(self, wnd, text):
        if text.endswith('\n'):
            text = text[:-1]

        self.put_string(wnd, text)
        wnd.screen.selection.clear()
        hist = kaa.app.config.hist('pyconsole_script', self.MAX_HISTORY)
        hist.add(text)

        f, t = self.document.marks['current_script']
        s = wnd.document.gettext(f, t)
        if '\n' in s:
            self._show_inputline(wnd, s)

    MAX_HISTORY = 100

    @commandid('python.script-history')
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


inputline_keys = {
    (alt, '\r'): ('inputline'),
    (alt, '\n'): ('inputline'),
}


class PythonInputlineMode(dialogmode.DialogMode, pythonmode.PythonMode):
    DEFAULT_STATUS_MSG = 'Hit alt+Enter to execute script.'

    DOCUMENT_MODE = False
    autoshrink = True
    USE_UNDO = True
    auto_indent = True
    border = True

    PYTHONINPUTLINE_KEY_BINDS = [
        inputline_keys
    ]

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.PYTHONINPUTLINE_KEY_BINDS)

    def init_tokenizers(self):
        pythonmode.PythonMode.init_tokenizers(self)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)
        wnd.cursor.setpos(self.document.endpos())
        kaa.app.messagebar.set_message('')

    def on_esc_pressed(self, wnd, event):
        # todo: run callback
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("Canceled")

    @commandid('inputline')
    @norec
    @norerun
    def input_line(self, w):
        s = self.document.gettext(0, self.document.endpos())
        target = self.target

        # close before execute
        popup = w.get_label('popup')
        popup.destroy()

        target.document.mode.exec_str(target, s)
        kaa.app.messagebar.set_message("")

    @classmethod
    def build(cls, target, s):
        doc = document.Document()
        doc.append(s)
        mode = cls()
        doc.setmode(mode)
        mode.target = target
        return doc


def show_console():
    cons = document.Document()
    mode = PythonConsoleMode()
    cons.setmode(mode)
    cons.set_title('<Python console>')

    kaa.app.show_doc(cons)
    kaa.app.messagebar.set_message('')
