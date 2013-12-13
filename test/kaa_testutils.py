import unittest.mock
from unittest.mock import patch

import kaa
import kaa.config
import kaa.options
from kaa import screen, document, cursor, context, editmode, fileio
from kaa.filetype.default import defaultmode


class _DmyWnd(context.Context):
    closed = False

    def __init__(self, scrn):
        self.screen = scrn
        self.cursor = cursor.Cursor(self)

    def activate(self):
        pass

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


class DmyFrame:
    closed = False

    def get_title(self):
        return 'title'

    def get_documents(self):
        return self.docs


class DmyApp(unittest.mock.Mock):
    option = kaa.options.build_parser().parse_args([])
    config = kaa.config.Config(option)
    config.hist_storage = unittest.mock.Mock()

    last_dir = ''
    DEFAULT_THEME = 'basic'
    storage = fileio.FileStorage()
    NUM_NEWFILE = 1

    def translate_key(self, mod, char):
        return (mod, char)

    def get_current_theme(self):
        return 'default'

    def translate_theme(self, theme):
        pass

    def set_focus(self, wnd):
        pass

kaa.app = DmyApp()



class _TestDocBase:
    DEFAULTMODECLASS = defaultmode.DefaultMode

    def get_title(self):
        return repr(self)

    def _getdoc(self, s=''):
        mode = self._getmode()
        return kaa.app.storage.newfile(mode, s)

    def _getmode(self):
        cls = self._getmodeclass()
        return self._createmode(cls)

    def _getmodeclass(self):
        return self.DEFAULTMODECLASS

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
