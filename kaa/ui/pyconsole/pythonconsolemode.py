import sys, traceback
from contextlib import contextmanager
import kaa
from kaa import document
from kaa.keyboard import *
from kaa.filetype.default import defaultmode
from kaa.filetype.python import pythonmode
from kaa.command import command, Commands, norec, norerun
from kaa.theme import Theme, Style

pythonconsole_keys = {
    (alt, '\r'): ('python.exec'),
    (alt, '\n'): ('python.exec'),
}

PythonConsoleThemes = {
    'basic':
        Theme([
            Style('stdout', 'Default', 'Default'),
            Style('stderr', 'Magenta', 'Default'),
        ]),
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
        style_stdout = output.mode.get_styleid('stdout')
        style_stderr = output.mode.get_styleid('stderr')
        
        class out:
            def __init__(self, style):
                self.style = style
                
            def write(self, s):
                if not output.closed:
                    output.append(s, self.style)
                    w = output.wnds[0]
                    if not w.closed:
                        # rebuild screen before move cursor
                        w.screen.locate(w.screen.pos, top=True)
                        w.cursor.eof()
                
        sys.stdout = out(style_stdout)
        sys.stderr = out(style_stderr)

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
        is_sel = wnd.screen.selection.is_selected()
        if is_sel:
            f, t = wnd.screen.selection.get_selrange()
            s = wnd.document.gettext(f, t)
        else:
            s = wnd.document.gettext(0, wnd.document.endpos())
        
        s = s.rstrip()
        if not s:
            return

        scr = s+'\n'

        with self._redirect_output():
            if not self._eval_str(s):
                self._exec_str(s)

        if not is_sel:
            endpos = self.document.endpos()
            if not self.document.gettext(endpos-1, endpos).endswith('\n'):
                self.edit_commands.insert_string(wnd, self.document.endpos(),
                    '\n', update_cursor=False)
            wnd.screen.selection.set_range(0, endpos)
            
class PythonOutputMode(defaultmode.DefaultMode):
    MODENAME = 'Python outputs'
    DOCUMENT_MODE = False
    USE_UNDO = False

    def init_themes(self):
        super().init_themes()
        self.themes.append(PythonConsoleThemes)


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

    frame = kaa.app.show_doc(cons).get_label('frame')
    frame.splitter.split(vert=False, doc=output)

    kaa.app.messagebar.set_message('Hit alt+Enter to execute script.')
