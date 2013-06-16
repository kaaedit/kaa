import curses
import kaa
from kaa import LOG
from . import keydef, color, dialog
from kaa import keyboard, document, macro
from kaa.ui.messagebar import messagebarmode


import curses.panel
def dump_panel():
    _trace('------------------------------------------')
    wnds = [w for w in kaa.app.mainframe.walk_children()]
    panel = curses.panel.top_panel()
    while panel:
        wnd = panel.window()
        t, l = wnd.getbegyx()
        h, w = wnd.getmaxyx()
        for ww in wnds:
            if ww._cwnd is wnd:
                pw = ww
                break
        else:
            if kaa.app.mainframe._cwnd is wnd:
                pw = kaa.app.mainframe
            else:
                pw='<error>'

        mode = ''
        if hasattr(pw, 'document'):
            mode = pw.document.mode
        _trace((l,t, l+w, t+h), panel.hidden(), pw, mode)
        panel = panel.below()

class CuiApp:
    def __init__(self):
        self._idleprocs = None
        self.colors = color.Colors()
        self.menus = []
        self.focus = None
        self.clipboard = ''
        self._quit = False

    def init(self, mainframe):
        self.messagebar = messagebarmode.MessageBarMode()

        buf = document.Buffer()
        doc = document.Document(buf)
        doc.setmode(self.messagebar)
        doc.insert(0, 'ready')
        mainframe.set_messagebar(doc)

        self.mainframe = mainframe
        self.focus = self.mainframe
        self.macro = macro.Macro()

    def quit(self):
        self._quit = True

    def on_idle(self):
        if not self._idleprocs:
            self._idleprocs = [
                doc.mode.on_idle for doc in document.Document.all]

        if self._idleprocs:
            proc = self._idleprocs.pop(0)
            # proc() returns True if proc() still has job to be done.
            if proc():
                self._idleprocs.append(proc)
                return True

        if self._idleprocs:
            return True

    def translate_theme(self, theme):
        for style in theme.styles.values():
            fg, bg = (color.ColorName.get(style.fgcolor.upper()),
                      color.ColorName.get(style.bgcolor.upper()))
            attr = self.colors.get_color(fg, bg)
            style.cui_colorattr = attr

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
                raise kaa.KaaError(
                    'Cannot use shift key for character: {!r}'.format((mod, c)))
            if ctrl:
                c = c.upper()
                if not (0x40 <= ord(c) <= 0x5f):
                    raise kaa.KaaError(
                        'Cannot use control key for character: {!r}'.format((mod, c)))
                return meta+chr(ord(c)-0x40)
            else:
                return meta+c
        else:
            ret = keydef.keyfromname(c, ctrl, shift)
            if ret is None:
                raise kaa.KaaError(
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
        self.mainframe.show_doc(doc)

    def show_inputline(self, doc):
        dlg = dialog.DialogWnd(parent=self.mainframe, doc=doc)
        self.mainframe.show_inputline(dlg)
        return dlg

    def show_dialog(self, doc):
        dlg = dialog.DialogWnd(parent=self.mainframe, doc=doc)
        self.mainframe.show_dialog(dlg)
        return dlg

    def show_menu(self, wnd, doc, root):
        if root:
            self.menus = [doc]
        else:
            self.menus.append(doc)
        return self.show_dialog(doc)

    def pop_menu(self):
        if self.menus:
            menu = self.menus.pop()
            menu.close()

        if self.menus:
            self.show_dialog(self.menus[-1])

    def clear_menu(self):
        self.menus = []

    def get_frames(self):
        return self.mainframe.childframes[:]

    def get_activeframe(self):
        assert self.mainframe.activeframe
        return self.mainframe.activeframe

    def run(self):
        self.mainframe.on_console_resized()
        nonblocking = True
        while not self._quit:
            try:
                inputs = self.focus.do_input(nonblocking)
                for c in inputs:
                    if isinstance(c, keydef.KeyEvent):
                        nonblocking = True
                        if c.key == curses.KEY_RESIZE:
                            self.mainframe.on_console_resized()
                            continue

                        # esc key pressed?
                        if c.key == '\x1b' and c.no_trailing_char:
                            self.focus.on_esc_pressed(c)
                        else:
                            self.focus.on_keyevent(c)

                if not inputs:
                    if self.mainframe.on_idle():
                        continue
                    # no input
                    if not self.on_idle():
                        # No more idle jobs
                        nonblocking = False

            except Exception as e:
                LOG.error('Unhandled exception', exc_info=True)
                kaa.app.messagebar.set_message(str(e))
#                raise


