import code
import sys
import traceback
from contextlib import contextmanager
import kaa
from kaa import document
from kaa.keyboard import *
from kaa.filetype.default import defaultmode
from kaa.filetype.python import pythonmode
from kaa.command import command, Commands, norec, norerun
from kaa.theme import Theme, Style
from kaa.ui.dialog import dialogmode
from kaa.ui.inputline import inputlinemode

pythonconsole_keys = {
    ('\r'): ('python.exec'),
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

class PythonConsoleMode(pythonmode.PythonMode):
    MODENAME = 'Python console'
    DOCUMENT_MODE = False

    PYTHONCONSOLE_KEY_BINDS = [
        pythonconsole_keys,
    ]

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.PYTHONCONSOLE_KEY_BINDS)

    def init_themes(self):
        super().init_themes()
        self.themes.append(PythonConsoleThemes)

    def init_tokenizers(self):
        pass

    def on_set_document(self, document):
        super().on_set_document(document)
        self.document.marks['current_script'] = (0, 0)
        self.interp = KaaInterpreter()
        
        self.document.append('>>>', self.get_styleid('ps'))
        self.document.append('\n', self.get_styleid('default'))
        p = self.document.endpos()
        self.document.marks['current_script'] = (p, p)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        cursor = dialogmode.DialogCursor(wnd,
                     [dialogmode.MarkRange('current_script')])
        wnd.set_cursor(cursor)
        f, t = self.document.marks['current_script']
        wnd.cursor.setpos(f)

    def on_esc_pressed(self, wnd, event):
        f, t = self.document.marks['current_script']
        self.document.delete(f, t)
        wnd.cursor.setpos(f)
        self.document.undo.clear()

    @contextmanager
    def _redirect_output(self, wnd):
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

        sys.stdout = out(self.document, style_stdout)
        sys.stderr = out(self.document, style_stderr)

        yield

        sys.stdout = stdout
        sys.stderr = stderr

    @command('python.exec')
    @norec
    @norerun
    def exec_script(self, wnd):
        self.document.undo.clear()
        f, t = self.document.marks['current_script']
        s = wnd.document.gettext(f, t)
        with self._redirect_output(wnd):
            ret = self.interp.runsource(s)
            if not ret:
                self.document.append('>>>', self.get_styleid('ps'))
                self.document.append('\n', self.get_styleid('default'))
                p = self.document.endpos()
                self.document.marks['current_script'] = (p, p)
                wnd.cursor.setpos(p)
            else:
                doc = PythonInputlineMode.build(wnd, s)
                kaa.app.show_dialog(doc)


    def exec_str(self, wnd, s):
        s = s.rstrip()+'\n'
        f, t = self.document.marks['current_script']
        self.document.replace(f, t, s, 
                style=self.get_styleid('default'))
        self.exec_script(wnd)

inputline_keys = {
    (alt, '\r'): ('inputline'),
    (alt, '\n'): ('inputline'),
}

class PythonInputlineMode(dialogmode.DialogMode, pythonmode.PythonMode):
    DOCUMENT_MODE = False
    autoshrink = True
    USE_UNDO = True
    auto_indent = True

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

    def on_esc_pressed(self, wnd, event):
        # todo: run callback
        super().on_esc_pressed(wnd, event)
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("Canceled")

    @command('inputline')
    @norec
    @norerun
    def input_line(self, w):
        s = self.document.gettext(0, self.document.endpos())
        target = self.target

        # close before execute
        popup = w.get_label('popup')
        popup.destroy()

        target.document.mode.exec_str(target, s)

    @classmethod
    def build(cls, target, s):
        buf = document.Buffer()
        doc = document.Document(buf)
        doc.append(s)
        mode = cls()
        doc.setmode(mode)
        mode.target = target
        return doc


def show_console():
    buf = document.Buffer()
    cons = document.Document(buf)
    mode = PythonConsoleMode()
    cons.setmode(mode)
    cons.set_title('<Python console>')

    kaa.app.show_doc(cons)
#    kaa.app.messagebar.set_message('Hit alt+Enter to execute script.')
