from unittest.mock import patch

import kaa
import kaa.config
from kaa import screen, document, cursor, context, editmode
from kaa.filetype.default import defaultmode

class _DmyWnd(context.Context):
    def __init__(self, scrn):
        self.screen = scrn
        self.cursor = cursor.Cursor(self)

    def set_editmode(self, editmode):
        self.editmode = editmode

    def get_context_parent(self):
        return None

    def locate_cursor(self, pos, top=None, middle=None, bottom=None):
        return pos, 0, 0

    def locate(self, pos, top=False, middle=False, bottom=False, align_always=False):
        return self.screen.locate(pos, top, middle, bottom, align_always)

    def update_window(self):
        pass

    def on_document_updated(self, pos, inslen, dellen):
        self.screen.on_document_updated(pos, inslen, dellen)

    def linedown(self):
        return self.screen.linedown()

    def lineup(self):
        return self.screen.lineup()

    def pagedown(self):
        return self.screen.pagedown()

    def pageup(self):
        return self.screen.pageup()

class DmyApp:
    config = kaa.config.Config()

    def translate_key(self, mod, char):
        return ()

    def get_current_theme(self):
        return 'default'

    def translate_theme(self, theme):
        pass

class _TestDocBase:
    def get_title(self):
        return repr(self)

    def _getdoc(self, s=''):
        import kaa
        if not hasattr(kaa, 'app'):
            kaa.app = DmyApp()
        mode = self._getmode()
        import kaa.fileio
        return kaa.fileio.newfile(mode, s)

    def _getmode(self):
        with patch('kaa.app', create=True):
            kaa.app.DEFAULT_THEME = 'default'
            cls = self._getmodeclass()
            return self._createmode(cls)

    def _getmodeclass(self):
        return defaultmode.DefaultMode

    def _createmode(self, cls):
        return cls()

class _TestScreenBase(_TestDocBase):
    def _getscreen(self, s, width=10, height=30, nowrap=False, show_lineno=False):
        scrn = screen.Screen()
        doc = self._getdoc(s)
        doc.mode.SHOW_LINENO = show_lineno
        scrn.set_document(doc)
        scrn.nowrap = nowrap
        scrn.setsize(width, height)
        scrn.locate(0, top=True)
        return scrn

    def _getwnd(self, s, width=10, height=30):
        scrn = self._getscreen(s, width, height)

        wnd = _DmyWnd(scrn)
        wnd.document = scrn.document
        wnd.document.add_window(wnd)

        wnd.cursor = cursor.Cursor(wnd)

        return wnd
