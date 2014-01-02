import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist
from kaa.command import commandid, norec, norerun
from kaa.keyboard import *


class WordCompleteList(filterlist.FilterListMode):
    MAX_INPUT_HEIGHT = 4
    MAX_CAPTION_LEN = 30
    USE_PHRASE_STYLE = True

    INITIAL_MESSAGE = "Hit tab/shift+tab to complete."
    border = True

    def calc_position(self, wnd):
        l, t, r, b = super().calc_position(wnd)
        height = b - t
        cury, curx = self.orgloc
        if self.stack_upper:
            top = max(0, cury - height - 1)
        else:
            top = cury + 2

        return l, top, r, top + height

    def on_esc_pressed(self, wnd, event):
        super().on_esc_pressed(wnd, event)
        wnd.get_label('popup').destroy()

    def start(self, wnd):
        self.orgpos = self.target.cursor.pos

        self.wordpos = (self.orgpos, self.orgpos)
        self.set_candidates(['aaaaa', 'bbbbbbbbbbbbbbb', 'cccccccccccccccccc'])

        editor = wnd.get_label('editor')
        self.set_query(editor, '')

        wnd.on_console_resized()

        self.target.activate()
        wnd.bring_top()
        editor.bring_top()


def show_wordlist(wnd):
    doc = WordCompleteList.build()
    doc.mode.orgloc = wnd.get_cursor_loc()
    doc.mode.target = wnd

    if doc.mode.orgloc[0] > (wnd.mainframe.height // 2):
        doc.mode.stack_upper = True
    else:
        doc.mode.stack_upper = False

    dlg = kaa.app.show_dialog(doc)

    doc.mode.start(dlg)

    return dlg
