from unittest.mock import patch

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

    def locate_cursor(self, pos):
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


class _TestDocBase:
    def _getbuf(self, s=''):
        buf = document.Buffer()
        buf.insert(0, s)
        return buf

    def _getdoc(self, s=''):
        doc = document.Document(self._getbuf(s))
        doc.setmode(self._getmode())
        return doc

    def _getmode(self):
        with patch('kaa.app', create=True):
            cls = self._getmodeclass()
            return self._createmode(cls)

    def _getmodeclass(self):
        return defaultmode.DefaultMode

    def _createmode(self, cls):
        return cls()

class _TestScreenBase(_TestDocBase):
    def _getscreen(self, s, width=10, height=30, nowrap=False):
        scrn = screen.Screen()
        scrn.set_document(self._getdoc(s))
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
