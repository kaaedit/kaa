import curses
import kaa
import kaa.log
from . import keydef, color, dialog
from kaa import config, keyboard, document, macro
from kaa.ui.messagebar import messagebarmode

from kaa.exceptions import KaaError

class CuiApp:
    SHOW_MENU_MESSAGE = 'Type F1 or alt+/ for menu.'
    DEFAULT_THEME = 'basic'
    DEFAULT_PALETTE = 'dark'
    MAX_CLIPBOARD = 10
    
    def __init__(self, config):
        self.config = config
        self.colors = None
        self._idleprocs = None
        self.lastcommands = ()
        self.focus = None
        self._clipboard = []
        self._quit = False
        self.theme = self.DEFAULT_THEME
        self.last_dir = '.'

    def init(self, mainframe):
        if self.config.palette:
            self.set_palette(self.config.palette)
        elif not self.colors:
            self.set_palette(self.DEFAULT_PALETTE)
            
        self.config.init_history()
        
        self.messagebar = messagebarmode.MessageBarMode()

        buf = document.Buffer()
        doc = document.Document(buf)
        doc.setmode(self.messagebar)
        mainframe.set_messagebar(doc)

        self.mainframe = mainframe
        self.focus = self.mainframe
        self.macro = macro.Macro()

        self.mainframe.on_console_resized()
        self.messagebar.set_message(self.SHOW_MENU_MESSAGE)

    def on_shutdown(self):
        self.config.hist_files.close()
        self.config.hist_dirs.close()
        self.config.hist_searchstr.close()
        self.config.hist_replstr.close()

        self.config.hist_grepstr.close()
        self.config.hist_grepdir.close()
        self.config.hist_grepfiles.close()

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

    def on_idle(self):
        if not self._idleprocs:
            self._idleprocs = [
                doc.mode.on_idle for doc in document.Document.all if doc.mode]

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
            fg, bg = (self.colors.colornames.get(style.fgcolor.upper()),
                      self.colors.colornames.get(style.bgcolor.upper()))
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
                raise KaaError(
                    'Cannot use shift key for character: {!r}'.format((mod, c)))
            if ctrl:
                c = c.upper()
                if not (0x40 <= ord(c) <= 0x5f):
                    raise KaaError(
                        'Cannot use control key for character: {!r}'.format((mod, c)))
                return meta+chr(ord(c)-0x40)
            else:
                return meta+c
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
        return self.mainframe.show_doc(doc)

    def show_inputline(self, doc):
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

    def get_clipboard(self):
        return self._clipboard[0] if self._clipboard else ''
        
    def get_clipboards(self):
        return iter(self._clipboard)
        
    def set_clipboard(self, s):
        self._clipboard.insert(0, s)
        del self._clipboard[self.MAX_CLIPBOARD:]

    def run(self):

        nonblocking = True
        while not self._quit:
            try:
                if not self.focus:
                    kaa.log.error('Internal error: invalid focus window.')
                    break
                inputs = self.focus.do_input(nonblocking)
                for c in inputs:
                    if isinstance(c, keydef.KeyEvent):
                        nonblocking = True
                        if c.key == curses.KEY_RESIZE:
                            self.mainframe.on_console_resized()
                            continue

                        if self.focus.editmode:
                            self.focus.editmode.on_keyevent(self.focus, c)

                if not inputs:
                    if self.mainframe.on_idle():
                        continue
                    # no input
                    if not self.on_idle():
                        # No more idle jobs
                        nonblocking = False

            except Exception as e:
                kaa.log.error('Unhandled exception', exc_info=True)
                kaa.app.messagebar.set_message(str(e))

                nonblocking = True

