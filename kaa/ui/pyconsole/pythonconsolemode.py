import sys, traceback
from contextlib import contextmanager
import kaa
from kaa import document
from kaa.keyboard import *
from kaa.filetype.default import defaultmode
from kaa.filetype.python import pythonmode
from kaa.command import command, Commands, norec, norerun

pythonconsole_keys = {
    (alt, '\r'): ('python.exec'),
    (alt, '\n'): ('python.exec'),
}

class PythonConsoleMode(pythonmode.PythonMode):
    MODENAME = 'Python console'
    DOCUMENT_MODE = False

    PYTHONCONSOLE_KEY_BINDS = [
        pythonconsole_keys,
    ]

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, self.PYTHONCONSOLE_KEY_BINDS)

    @contextmanager
    def _redirect_output(self):
        stdout = sys.stdout
        stderr = sys.stderr

        output = self.output
        
        class out:
            def write(self, s):
                if not output.closed:
                    output.append(s)
                    w = output.wnds[0]
                    if not w.closed:
                        # rebuild screen before move cursor
                        w.screen.locate(w.screen.pos, top=True)
                        w.cursor.eof()
                
        sys.stdout = out()
        sys.stderr = out()

        yield
        
        sys.stdout = stdout
        sys.stderr = stderr

    def _eval_str(self, s):
        try:
            comp = compile(s,  '<interactive input>','eval')
        except SyntaxError:
            return

        try:
            import __main__
            ret = eval(comp, __main__.__dict__, __main__.__dict__)
            if ret is not None:
                print(repr(ret))
        except Exception:
            traceback.print_exc()
            return True

        return True

    def _exec_str(self, s):
        try:
            comp = compile(s,  '<interactive input>','exec')
        except SyntaxError:
            traceback.print_exc()
            return

        try:
            import __main__
            exec(comp, __main__.__dict__, __main__.__dict__)
        except Exception:
            traceback.print_exc()
            return True

        return True

    @command('python.exec')
    @norec
    @norerun
    def exec_script(self, wnd):
        if wnd.screen.selection.is_selected():
            f, t = wnd.screen.selection.get_range()
            s = wnd.document.gettext(f, t)
        else:
            s = wnd.document.gettext(0, wnd.document.endpos())

        s = s.rstrip()
        if not s:
            return

        s += '\n'

        with self._redirect_output():
            if not self._eval_str(s):
                self._exec_str(s)


class PythonOutputMode(defaultmode.DefaultMode):
    MODENAME = 'Python outputs'
    DOCUMENT_MODE = False
    USE_UNDO = False

def show_console():
    buf = document.Buffer()
    cons = document.Document(buf)
    mode = PythonConsoleMode()
    cons.setmode(mode)
    cons.set_title('<Python console>')

    buf = document.Buffer()
    output = document.Document(buf)
    mode = PythonOutputMode()
    output.setmode(mode)
    output.set_title('<Python output>')

    cons.mode.output = output

    frame = kaa.app.show_doc(cons)
    frame.splitter.split(vert=False, doc=output)

    kaa.app.messagebar.set_message('Hit alt+Enter to execute script.')
