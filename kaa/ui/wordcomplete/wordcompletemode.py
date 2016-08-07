import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist
from kaa.command import commandid, norec, norerun
from kaa.keyboard import *


class WordCompleteList(filterlist.FilterListMode):
    MAX_CAPTION_LEN = 30
    USE_PHRASE_STYLE = True

    def _filter_items(self, query):
        if query:
            query = query.upper()
            items = []
            for s in self.candidates:
                u = s.text.upper()
                if u.startswith(query):
                    items.append(s)
        else:
            items = self.candidates[:]

        sel = items[0] if items else None
        return sel, items


workcomplete_keys = {
    tab: 'filterlistdlg.next',
    (shift, tab): 'filterlistdlg.prev',
    '\r': 'wordcomplete.select',
    '\n': 'wordcomplete.select',
}


class WordCompleteInputMode(filterlist.FilterListInputDlgMode):
    MAX_INPUT_HEIGHT = 4
    INITIAL_MESSAGE = "Hit tab/shift+tab to complete."

    @classmethod
    def build(cls, target):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)
        mode.target = target

        with dialogmode.FormBuilder(doc) as f:
            f.append_text('caption', 'Select word:')
            f.append_text('default', ' ')
            f.append_text('default', '', mark_pair='query')

        return doc

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(workcomplete_keys)

    def calc_position(self, wnd):
        w, h = wnd.getsize()
        height = self.calc_height(wnd)
        height = min(height, self.MAX_INPUT_HEIGHT)

        cury, curx = self.orgloc
        if self.stack_upper:
            top = max(0, cury - height - 1)
        else:
            top = cury + 2

        return 0, top, wnd.mainframe.width, top + height

    @commandid('wordcomplete.select')
    @norec
    @norerun
    def selected(self, wnd):
        self.target.screen.selection.clear()
        list = wnd.get_label('dlg_filterlist')
        sel = list.document.mode.cursel
        if sel:
            s = sel.value
        else:
            s = self.get_query()

        self.target.document.mode.replace_string(
            self.target, self.wordpos[0], self.wordpos[1],
            s, update_cursor=True)
        wnd.get_label('popup').destroy()

        if self.callback:
            self.callback(self.wordpos[0] + len(s))

    def on_edited(self, wnd):
        super().on_edited(wnd)
        s = self.get_query()
        f, t = self.wordpos
        self.target.document.mode.replace_string(
            self.target, f, t, s, update_cursor=True)
        self.wordpos = (f, f + len(s))

    def on_esc_pressed(self, wnd, event):
        self.target.screen.selection.clear()
        super().on_esc_pressed(wnd, event)

    def _get_target_word(self, orgpos):
        word = self.target.document.mode.get_word_at(orgpos)
        if word:
            f, t, cg = word
            if f < t and cg[0] in 'LMN':  # Letter, Mark, Number
                return (f, t)
            elif orgpos != 0 and orgpos == f and (cg[0] not in 'LMN'):
                # cursor is at top of non-word char.
                # check if we are at end of word.
                prev = self.target.document.mode.get_word_at(orgpos-1)
                if prev:
                    pf, pt, pcg = prev
                    if pt == orgpos and (pcg[0] in 'LMN'):
                        # select previous word
                        return (pf, pt)
        return (orgpos, orgpos)

    def start(self, list):
        self.orgpos = self.target.cursor.pos

        self.wordpos = self._get_target_word(self.orgpos)
        wnd = self.document.wnds[0]

        curword = self.target.document.gettext(*self.wordpos)
        if curword:
            self.target.screen.selection.set_range(*self.wordpos)
            self.set_query(wnd, curword)

        # build word list
        # word at cursor position should not appear in the list.
        words = [w for w in self.target.document.mode.get_word_list()
                 if w != curword]

        list.document.mode.set_candidates(words)
        list.document.mode.candidates.sort(key=lambda v: v.text.upper())
        list.document.mode.set_query(list, self.get_query())
        list.get_label('popup').on_console_resized()


def show_wordlist(wnd):
    doc = WordCompleteInputMode.build(wnd)
    doc.mode.orgloc = wnd.get_cursor_loc()

    if doc.mode.orgloc[0] > (wnd.mainframe.height // 2):
        doc.mode.stack_upper = True
    else:
        doc.mode.stack_upper = False

    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = WordCompleteList.build()
    filterlistdoc.mode.SEP = ' '
    list = dlg.add_doc('dlg_filterlist', 0, filterlistdoc)

    doc.mode.start(list)

    return dlg
