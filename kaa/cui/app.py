import os
import signal
import gc
import time
import sys
import select
import curses
import threading
import contextlib

import kaa
import kaa.log
from . import keydef, color, dialog
from kaa import clipboard
from kaa import document
from kaa import keyboard
from kaa import macro

from kaa.exceptions import KaaError


class CuiApp:
    DEFAULT_MENU_MESSAGE = 'Type F1 or alt+m for menu.'
    DEFAULT_THEME = 'basic'
    DEFAULT_PALETTE = 'dark'
    NUM_NEWFILE = 1

    def __init__(self, config):
        self.config = config
        self.clipboard = clipboard.select_clipboard()
        self.colors = None
        self._idleprocs = None
        self.lastcommands = ()
        self.focus = None
        self._quit = False
        self.theme = self.DEFAULT_THEME
        self.last_dir = '.'
        self._input_readers = []

        self._lock = threading.RLock()
        self._tasks = []

        self.commands = {}
        self.is_availables = {}

        self.sigwinch_rfd, self.sigwinch_wfd = os.pipe()
        signal.signal(signal.SIGWINCH,
                      lambda *args: os.write(self.sigwinch_wfd, b'0'))

    def register_commandobj(self, cmds):
        self.commands.update(cmds.get_commands())
        self.is_availables.update(cmds.get_commands_is_enable())

    def init_commands(self):
        from kaa.commands import appcommand, toolcommand, filecommand, gitcommand

        self.app_commands = appcommand.ApplicationCommands()
        self.register_commandobj(self.app_commands)

        self.file_commands = filecommand.FileCommands()
        self.register_commandobj(self.file_commands)

        self.register_commandobj(toolcommand.ToolCommands())
        self.register_commandobj(appcommand.MacroCommands())
        self.register_commandobj(gitcommand.GitCommands())

        for name in dir(self):
            attr = getattr(self, name)
            if hasattr(attr, 'COMMAND_ID') and callable(attr):
                self.commands[getattr(attr, 'COMMAND_ID')] = attr

    def init(self, mainframe):
        self.init_commands()

        if self.config.palette:
            self.set_palette(self.config.palette)
        elif not self.colors:
            self.set_palette(self.DEFAULT_PALETTE)

        self.config.init_history()

        from kaa.ui.messagebar import messagebarmode
        self.messagebar = messagebarmode.MessageBarMode()

        doc = document.Document()
        doc.setmode(self.messagebar)
        mainframe.set_messagebar(doc)

        self.mainframe = mainframe
        self.focus = self.mainframe
        self.macro = macro.Macro()

        self.mainframe.on_console_resized()
        self.messagebar.set_message(self.DEFAULT_MENU_MESSAGE)

    def on_shutdown(self):
        os.close(self.sigwinch_rfd)
        os.close(self.sigwinch_wfd)
        self.config.close()

    def get_current_theme(self):
        return self.theme

    def set_palette(self, name):
        palette = self.get_palette(name)
        self.colors = color.Colors(palette)

    def get_palette(self, name):
        if name == 'light':
            return color.LightPalette()
        else:
            return color.DarkPalette()

    def quit(self):
        self._quit = True

    def call_later(self, secs, f, *args, **kwargs):
        with self._lock:
            self._tasks.append((time.time() + secs, f, args, kwargs))

    SCHEDULE_WAIT_MARGIN = 0.05

    def _next_scheduled_task(self):
        with self._lock:
            tasks = sorted(t for t, f, a, k in self._tasks)
            if tasks:
                wait = max(0, tasks[0] - time.time())
                return wait + wait * self.SCHEDULE_WAIT_MARGIN

    def _run_scheduled_task(self):
        with self._lock:
            now = time.time()
            for n, (t, f, a, k) in enumerate(self._tasks):
                if t <= now:
                    del self._tasks[n]
                    f(*a, **k)
                    return

    def get_command(self, commandid):
        cmd = self.commands.get(commandid, None)
        if cmd:
            is_available = self.is_availables.get(commandid, None)
            return (is_available, cmd)

    def set_idlejob(self):
        self._idleprocs = [
            doc.mode.on_idle for doc in document.Document.all if doc.mode]

    def on_idle(self):
        if self._idleprocs:
            proc = self._idleprocs.pop(0)
            # proc() returns True if proc() still has job to be done.
            if proc():
                self._idleprocs.append(proc)

            return True
        else:
            return False

    def translate_theme(self, theme):
        overlays = {}
        for name, overlay in theme.overlays.items():
            fg = bg = None
            if overlay.fgcolor:
                fg = self.colors.colornames.get(overlay.fgcolor.upper())
            if overlay.bgcolor:
                bg = self.colors.colornames.get(overlay.bgcolor.upper())
            overlays[name] = (fg, bg)

        for style in theme.styles.values():
            fg, bg = (self.colors.colornames.get(style.fgcolor.upper()),
                      self.colors.colornames.get(style.bgcolor.upper()))
            attr = self.colors.get_color(fg, bg)
            style.cui_colorattr = attr

            style.cui_overlays = {}
            for name, (o_fg, o_bg) in overlays.items():
                if o_fg is None:
                    o_fg = fg
                if o_bg is None:
                    o_bg = bg
                style.cui_overlays[name] = self.colors.get_color(o_fg, o_bg)

    def get_keyname(self, key):
        try:
            if not isinstance(key, int):
                key = ord(key)

            return str(curses.keyname(key), 'utf-8', 'replace')
        except Exception:
            return '?'

    def translate_key(self, mod, c):
        """Translate kaa's key value to curses keycode"""

        alt = keyboard.alt in mod
        ctrl = keyboard.ctrl in mod
        shift = keyboard.shift in mod

        if alt:
            meta = '\x1b'
        else:
            meta = ''

        if isinstance(c, str):
            if shift:
                raise KaaError(
                    'Cannot use shift key for character: {!r}'.format((mod, c)))
            if ctrl:
                c = c.upper()
                if not (0x40 <= ord(c) <= 0x5f):
                    raise KaaError(
                        'Cannot use control key for character: {!r}'.format((mod, c)))
                return meta + chr(ord(c) - 0x40)
            else:
                return meta + c
        else:
            ret = keydef.keyfromname(c, ctrl, shift)
            if ret is None:
                raise KaaError(
                    'Cannot convert character: {!r}'.format((mod, c)))

            return [ret] if not meta else [meta, ret]

    def set_focus(self, wnd):
        if wnd is self.focus:
            return

        if self.focus:
            self.focus.on_killfocus()

        self.focus = wnd
        if wnd:
            wnd.on_focus()

    def show_doc(self, doc):
        '''
        Create new window for the doc and show it.
        '''
        ret = self.mainframe.show_doc(doc)
        return ret

    def show_inputline(self, doc):
        self._idleprocs = None  # Reschedule idle procs
        dlg = dialog.DialogWnd(parent=self.mainframe, doc=doc)
        self.mainframe.show_inputline(dlg)
        return dlg

    def show_dialog(self, doc):
        dlg = dialog.DialogWnd(parent=self.mainframe, doc=doc)
        self.mainframe.show_dialog(dlg)
        return dlg

    def get_frames(self):
        return self.mainframe.childframes[:]

    def get_activeframe(self):
        return self.mainframe.activeframe

    def show_cursor(self, f):
        try:
            curses.curs_set(f)
        except curses.error:
            # curses.curs_set() occasionally fails if $TERM=xterm-color
            pass

    @contextlib.contextmanager
    def restore_teminal(self):
        curses.def_prog_mode()
        curses.endwin()
        try:
            yield
        finally:
            curses.reset_prog_mode()
            self.mainframe.refresh()

    def add_input_reader(self, reader):
        self._input_readers.append(reader)

    def del_input_reader(self, reader):
        if reader in self._input_readers:
            self._input_readers.remove(reader)

    def dump_panel(self):
        import curses.panel
        panels = []
        p = curses.panel.top_panel()
        while p:
            panels.append(p)
            p = p.below()

        for w in self.mainframe.walk_children():
            idx = panels.index(w._panel)
            d = getattr(w, 'document', w)
            m = getattr(d, 'mode', w)
            panels[idx] = m

    def run(self):
        #        def f(t, i):
        #            _trace(t, i)
        #        gc.callbacks.append(f)
        gc.set_threshold(2000, 10, 10)

        nonblocking = True
        while not self._quit:
            try:
                if not self.focus:
                    kaa.log.error('Internal error: invalid focus window.')
                    break

                self.focus.restore_cursor_pos()
                if not nonblocking:
                    # update screen before sleep.
                    curses.panel.update_panels()
                    curses.doupdate()

                rd = []
                for f in self._input_readers:
                    rd.extend(f.get_reader())

                try:
                    rlist, _, _ = select.select(
                        [sys.stdin, self.sigwinch_rfd] + rd, [], [],
                        0 if nonblocking else self._next_scheduled_task())

                except InterruptedError:
                    pass

                if not nonblocking and not rlist:
                    # timeout
                    self._run_scheduled_task()
                    self.set_idlejob()  # Reschedule idle procs

                if self.sigwinch_rfd in rlist:
                    os.read(self.sigwinch_rfd, 1)

                    # sigh. pep-0475 prevents us to handling SIGWINCH.
                    # force curses to resize window.
                    import struct
                    import fcntl
                    import termios
                    v = fcntl.ioctl(0, termios.TIOCGWINSZ,
                                    struct.pack('HHHH', 0, 0, 0, 0))
                    lines, cols, _, _ = struct.unpack('HHHH', v)
                    curses.resizeterm(lines, cols)
                    self.mainframe.on_console_resized()

                ready = [r for r in rlist if r not in
                         (sys.stdin, self.sigwinch_rfd)]
                if ready:
                    nonblocking = True
                    for r in ready:
                        idx = rd.index(r)
                        self._input_readers[idx].read_input(r)
                    self.set_idlejob()  # Reschedule idle procs

                inputs = self.focus.do_input(nonblocking=True)
                for c in inputs:
                    if isinstance(c, keydef.KeyEvent):
                        nonblocking = True
                        if c.key == curses.KEY_RESIZE:
                            self.mainframe.on_console_resized()
                            continue

                        if self.focus.editmode:
                            self.focus.editmode.on_keyevent(self.focus, c)
                            if self.focus:
                                self.focus.update_window()

                if not inputs:
                    if self.mainframe.on_idle():
                        self.set_idlejob()  # Reschedule idle procs
                        continue

                    # no input
                    if not self.on_idle():
                        # No more idle jobs
                        nonblocking = False
                else:
                    self.set_idlejob()  # Reschedule idle procs

            except Exception as e:
                kaa.log.error('Unhandled exception', exc_info=True)
                kaa.app.messagebar.set_message(' '.join(str(e).split('\n')))

                nonblocking = True
