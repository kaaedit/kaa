import re
import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import selectlist


from kaa.command import commandid, norec, norerun
from kaa.keyboard import *
import kaa.filetype.default.keybind


FilterListThemes = {
    'basic': [],
}


class FilterListMode(selectlist.SelectItemList):
    SEP = '\n'
    MAX_CAPTION_LEN = None
    USE_PHRASE_STYLE = False

    def init_themes(self):
        super().init_themes()
        self.themes.append(FilterListThemes)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)
        wnd.set_label('filterlist', wnd)

    def set_candidates(self, candidates):
        ws = re.compile(r'\s')
        self.candidates = []
        for c in candidates:
            phrase = False
            caption = c
            if ws.search(caption):
                phrase = True
                caption = ' '.join(caption.split())
                if not caption:
                    caption = '(...)'

            if self.MAX_CAPTION_LEN is not None:
                if len(caption) > self.MAX_CAPTION_LEN:
                    caption = caption[:self.MAX_CAPTION_LEN] + '...'
                    phrase = True

            if not self.USE_PHRASE_STYLE or not phrase:
                c = selectlist.SelectItem(
                    'selectitem', 'selectitem-active', caption, c)
            else:
                c = selectlist.SelectItem(
                    'selectphrase', 'selectphrase-active', caption, c)
            self.candidates.append(c)

    def _filter_items(self, query):
        query = [f.upper() for f in query.split()]
        if query:
            items = []
            for item in self.candidates:
                u = item.text.upper()
                for q in query:
                    if q not in u:
                        break
                else:
                    items.append(item)
        else:
            items = self.candidates[:]

        sel = items[0] if items else None
        return sel, items

    def set_query(self, wnd, query):
        sel, items = self._filter_items(query)
        self.update_doc(items)
        if sel:
            self.update_sel(wnd, sel)


FilterListInputDlgThemes = {
    'basic': [],
}


filterlistinputdlg_keys = {
    down: 'filterlistdlg.next',
    (ctrl, 'n'): 'filterlistdlg.next',
    tab: 'filterlistdlg.next',
    up: 'filterlistdlg.prev',
    (ctrl, 'p'): 'filterlistdlg.prev',
    (shift, tab): 'filterlistdlg.prev',
    '\r': 'filterlistdlg.select',
    '\n': 'filterlistdlg.select',
}


class FilterListInputDlgMode(dialogmode.DialogMode):
    MAX_INPUT_HEIGHT = 4
    callback = None
    INITIAL_MESSAGE = "Hit up/down to select item."
    NO_WRAPINDENT = False

    @classmethod
    def build(cls, caption, callback):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)

        mode.callback = callback

        with dialogmode.FormBuilder(doc) as f:
            f.append_text('caption', caption)
            f.append_text('default', ' ')
            f.append_text('default', '', mark_pair='query')

        return doc

    def init_themes(self):
        super().init_themes()
        self.themes.append(FilterListInputDlgThemes)

    def init_keybind(self):
        self.keybind.add_keybind(
            kaa.filetype.default.keybind.edit_command_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.cursor_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.emacs_keys)
        self.keybind.add_keybind(filterlistinputdlg_keys)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.CURSOR_TO_MIDDLE_ON_SCROLL = False
        cursor = dialogmode.DialogCursor(wnd,
                                         [dialogmode.MarkRange('query')])

        wnd.set_cursor(cursor)
        wnd.cursor.setpos(self.document.marks['query'][1])
        wnd.set_label('query_field', self)
        kaa.app.messagebar.set_message(self.INITIAL_MESSAGE)

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("")
        if self.callback:
            self.callback(None)

    def on_edited(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.set_query(wnd, self.get_query())
        filterlist.get_label('popup').on_console_resized()

    def get_query(self):
        f, t = self.document.marks['query']
        return self.document.gettext(f, t)

    def set_query(self, wnd, s):
        wnd.screen.selection.clear()
        f, t = self.document.marks['query']
        self.document.replace(f, t, s)
        wnd.cursor.setpos(f + len(s))

    @commandid('filterlistdlg.next')
    @norec
    @norerun
    def next(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.sel_next(filterlist)

    @commandid('filterlistdlg.prev')
    @norec
    @norerun
    def prev(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.sel_prev(filterlist)

    def _selected(self, wnd, value):
        popup = wnd.get_label('popup')
        popup.destroy()

        if self.callback:
            self.callback(value)

    @commandid('filterlistdlg.select')
    @norec
    @norerun
    def on_select(self, wnd):
        filterlist = wnd.get_label('filterlist')
        cur = filterlist.document.mode.cursel
        if cur:
            self._selected(wnd, cur.value)
            return True


def show_listdlg(title, candidates, callback):
    doc = FilterListInputDlgMode.build(
        title, callback)
    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = FilterListMode.build()
    list = dlg.add_doc('dlg_filterlist', 0, filterlistdoc)

    filterlistdoc.mode.set_candidates(candidates)
    filterlistdoc.mode.set_query(list, '')
    dlg.on_console_resized()

    return dlg
