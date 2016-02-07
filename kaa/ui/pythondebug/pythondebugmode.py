import os
import signal
import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.theme import Overlay
from kaa.theme import Style
from kaa.command import commandid, norec, norerun
from kaa.keyboard import *
from kaa.ui.selectlist import selectlist
import kaa.ui.pythondebug.port
from kaa.ui.inputline import inputlinemode


def show_expr(port, depth):
    def callback(w, s):
        s = s.strip()
        if s:
            kaa.app.config.hist('pythondebug_expr').add(s)
            port.show_expr(depth, s)

    hist = [s for s, info in kaa.app.config.hist('pythondebug_expr').get()]
    doc = inputlinemode.InputlineMode.build('Python expression:',
                                            callback, history=hist)
    kaa.app.show_dialog(doc)


breakpoints_keys = {
    'd': 'breakpoints.delete',
    (ctrl, 'h'): 'breakpoints.delete',
    delete: 'breakpoints.delete',
    backspace: 'breakpoints.delete',
}


class BreakPoints(selectlist.SelectItemList):
    SEP = '\n'
    caption = 'Break points'
    border = True

    @classmethod
    def build(cls, port):
        doc = super().build()
        doc.mode.show_breakpoints(port)
        kaa.app.messagebar.set_message("Hit 'd' key to remove breakpoint")
        return doc

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(breakpoints_keys)

    def show_breakpoints(self, port):
        self.port = port
        breakpoints = self.port.get_breakpoints()
        breakpoints.sort(key=lambda o: (o.filename, o.lineno))
        items = []
        for bp in breakpoints:
            caption = '{bp.filename}:{bp.lineno}'.format(bp=bp)
            c = selectlist.SelectItem(
                'selectitem', 'selectitem-active', caption, bp)
            items.append(c)

        self.update_doc(items)

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message('')

    @commandid('breakpoints.delete')
    @norec
    @norerun
    def delete_bp(self, wnd):
        if not self.cursel:
            return
        bp = self.cursel.value

        index = self.items.index(self.cursel)
        items = [item for item in self.items if item is not self.cursel]
        self.update_doc(items)
        if not self.items:
            sel = None
        elif index < len(self.items):
            sel = self.items[index]
        else:
            sel = self.items[-1]

        self.update_sel(wnd, sel)
        self.port.del_breakpoint(bp)
        self.port.display_breakpoints()

DebugThemes = {
    'basic': [
        Style('line', 'Orange', None),
        Style('filename', 'Cyan', None),
        Style('lineno', 'Cyan', None),
        Style('funcname', 'Cyan', None),
        Style('dirname', 'Cyan', None),
        Style('status', 'Base3', 'Red', nowrap=True),
        Overlay('current_stack', 'Black', 'Yellow'),
    ],
}


callstack_keys = {
    down: 'callstack_keys.next',
    (ctrl, 'n'): 'callstack_keys.next',
    (ctrl, 'f'): 'callstack_keys.next',
    tab: 'callstack_keys.next',
    up: 'callstack_keys.prev',
    (ctrl, 'p'): 'callstack_keys.prev',
    (ctrl, 'b'): 'callstack_keys.prev',
    (shift, tab): 'callstack_keys.prev',
}


class PythonStackList(dialogmode.DialogMode):
    SHOW_CURSOR = False
    autoshrink = True
    cursel = 0

    def init_themes(self):
        super().init_themes()
        self.themes.append(DebugThemes)

    def calc_height(self, wnd):
        height = wnd.screen.get_total_height(wnd.mainframe.height // 2)
        return height

    def build(self, stack):
        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())

        self.stack = tuple(stack or ())
        with dialogmode.FormBuilder(self.document) as f:
            for n, (fname, lno, funcname, lines) in enumerate(self.stack):
                s = self.document.endpos()

                f.append_text('funcname', funcname.replace('&', '&&'))
                f.append_text('default', ':')

                dirname, filename = os.path.split(fname)
                f.append_text('filename', filename.replace('&', '&&'))
                f.append_text('default', ':')

                f.append_text('lineno', str(lno))
                f.append_text('default', ':')

                f.append_text('dirname', dirname.replace('&', '&&') + '\n')

                line = (lines[0] if lines else '').strip()
                if not line:
                    line = '(empty line)'
                f.append_text('line', line.replace('&', '&&') + '\n')

                t = self.document.endpos()
                self.document.marks[('stack', n)] = (s, t)

    def update_sel(self, wnd, n):
        if self.cursel != n:
            f, t = self.document.marks.get(
                ('stack', self.cursel), (None, None))
            if f is not None:
                wnd.set_line_overlay(f, None)

        f, t = self.document.marks.get(('stack', n), (None, None))
        if f is not None:
            wnd.set_line_overlay(f, 'current_stack')

        self.cursel = n
        if n < len(self.stack):
            (fname, lno, funcname, lines) = self.stack[n]

            if f is not None:
                wnd.cursor.setpos(f, bottom=True)

            wnd.activate()
            debugpanel = wnd.get_label('editor')
            debugpanel.document.mode.show_line(fname, lno)
            debugpanel.activate()

    @commandid('callstack_keys.prev')
    @norec
    @norerun
    def stack_prev(self, wnd):
        if self.cursel:
            self.update_sel(wnd, self.cursel - 1)

    @commandid('callstack_keys.next')
    @norec
    @norerun
    def stack_next(self, wnd):
        if self.cursel < len(self.stack) - 1:
            self.update_sel(wnd, self.cursel + 1)


class PythonDebuggerPanel(dialogmode.DialogMode):
    SHOW_CURSOR = False
    autoshrink = True

    def init_themes(self):
        super().init_themes()
        self.themes.append(DebugThemes)

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(callstack_keys)

    def setup(self):
        super().setup()
        self.updated_wnds = set()

    def close(self):
        self._restore_highlight()
        super().close()
        self.port = None

    def on_str(self, wnd, s, overwrite=False):
        pass

    def build(self, stack):
        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())

        self.stack = tuple(stack or ())
        with dialogmode.FormBuilder(self.document) as f:
            f.append_text('button', '[&Step]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_step)

            f.append_text('button', '[&Next]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_next)

            f.append_text('button', '[&Return]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_return)

            f.append_text('button', '[&Continue]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_continue)

            f.append_text('button', '[&Expr]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_expr)

            f.append_text('button', '[&Kill]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_kill)

            f.append_text('button', '[&Breakpoint]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_breakpoint)

            f.append_text('button', '[&Quit]',
                          shortcut_style='button.shortcut',
                          on_shortcut=self.on_quit)

            f.append_text('status', '-Waiting-', mark_pair='status')

    def update(self, wnd, stack):
        self.build(stack)
        self.show_curline(wnd)

        w = self._get_stacklist(wnd)
        w.document.mode.build(stack)
        w.document.mode.update_sel(w, 0)

    def show_curline(self, wnd):
        if self.stack:
            (fname, lno, funcname, lines) = self.stack[0]
            self.show_line(fname, lno)
            wnd.activate()

            wnd.mainframe.on_console_resized()

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message('')

    def set_status(self, wnd, status):
        f, t = self.document.marks['status']
        styleid = self.get_styleid('status')
        self.document.replace(f, t, status, styleid)
        wnd.clear_line_overlay()
#        self.update_sel(wnd, 0)

    def _restore_highlight(self):
        for w in self.updated_wnds:
            w.clear_line_overlay()
        self.updated_wnds = set()

    def _locate_doc(self, wnd, doc, lineno):
        self._restore_highlight()

        pos = doc.get_lineno_pos(lineno)
        tol = doc.gettol(pos)

        wnd.clear_line_overlay()
        wnd.set_line_overlay(tol, 'current-row')

        wnd.screen.locate(tol, middle=True, align_always=True)
        wnd.cursor.setpos(tol, middle=True)
        wnd.activate()
        self.updated_wnds.add(wnd)

    def show_line(self, filename, lineno):
        filename = os.path.abspath(filename)
        doc = document.Document.find_filename(filename)
        if doc:
            wnd = doc.wnds[0]
            wnd.activate()
        else:
            doc = kaa.app.storage.openfile(filename, nohist=True)
            wnd = kaa.app.show_doc(doc)

        self._locate_doc(wnd, doc, lineno)

    msg_notbreaking = 'Debug target is not idle.'

    def _cmd_not_breaked(self):
        kaa.app.messagebar.set_message(self.msg_notbreaking)

    def on_step(self, wnd):
        if self.port.is_breaking():
            self.port.set_step()
        else:
            self._cmd_not_breaked()

    def on_next(self, wnd):
        if self.port.is_breaking():
            self.port.set_next()
        else:
            self._cmd_not_breaked()

    def on_return(self, wnd):
        if self.port.is_breaking():
            self.port.set_return()
        else:
            self._cmd_not_breaked()

    def on_continue(self, wnd):
        if self.port.is_breaking():
            self.port.set_continue()
        else:
            self._cmd_not_breaked()

    def on_expr(self, wnd):
        if self.port.is_breaking():
            show_expr(self.port, self._get_stacklist(wnd).document.mode.cursel)
        else:
            self._cmd_not_breaked()

    def on_kill(self, wnd):
        if not self.port.is_breaking():
            os.kill(self.port.kaadbg_pid, signal.SIGINT)
        else:
            msg = 'Debug target is idle.'
            kaa.app.messagebar.set_message(msg)

    def on_breakpoint(self, wnd):
        doc = BreakPoints.build(self.port)
        kaa.app.show_dialog(doc)

    def on_quit(self, wnd):
        self.port.close()

    def _get_stacklist(self, wnd):
        return wnd.get_label('dlg_stacklist')

    @commandid('callstack_keys.prev')
    @norec
    @norerun
    def stack_prev(self, wnd):
        w = self._get_stacklist(wnd)
        w.document.mode.stack_prev(w)

    @commandid('callstack_keys.next')
    @norec
    @norerun
    def stack_next(self, wnd):
        w = self._get_stacklist(wnd)
        w.document.mode.stack_next(w)


def show_callstack(port, stack):
    doc = document.Document()
    doc.set_title('Python call stack')
    mode = PythonDebuggerPanel()
    mode.port = port

    doc.setmode(mode)
    mode.build(stack)

    dlg = kaa.app.show_inputline(doc)
    ret = dlg.get_label('editor')

    stacklist = document.Document()
    stacklistmode = PythonStackList()
    stacklist.setmode(stacklistmode)
    stacklistmode.build(stack)

    wnd = dlg.add_doc('dlg_stacklist', 0, stacklist)
    stacklistmode.update_sel(wnd, 0)

    mode.show_curline(ret)

    return ret
