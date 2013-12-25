import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import selectlist, filterlist
from kaa.command import command, norec, norerun
from kaa.keyboard import *

texthist_keys = {
    '\r': 'texthist.select',
    '\n': 'texthist.select',
}


class TextHistMode(filterlist.FilterListMode):
    MAX_CAPTION_LEN = 256
    SCREEN_NOWRAP = True

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(texthist_keys)

    def set_candidates(self, candidates):
        self.candidates = []
        for c in candidates:
            caption = ' '.join(c.split())
            if not caption:
                caption = '(...)'
            if len(caption) > self.MAX_CAPTION_LEN:
                caption = caption[:self.MAX_CAPTION_LEN] + '...'
            c = selectlist.SelectItem(
                'selectitem', 'selectitem-active', caption, c)
            self.candidates.append(c)

    def _filter_items(self, query):
        if query:
            query = query.upper().split()
            items = []
            for s in self.candidates:
                u = s.value.upper()
                for q in query:
                    if q not in u:
                        break
                else:
                    items.append(s)
        else:
            items = self.candidates[:]

        sel = items[0] if items else None
        return sel, items

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("")
        self.callback(None)

    @command('texthist.select')
    @norec
    @norerun
    def on_selected(self, wnd):
        if self.cursel:
            self.callback(self.cursel.value)

        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("")

#            self.target.document.mode.put_string(
#                self.target, self.cursel.value)
#            self.target.screen.selection.clear()
#            kaa.app.text.set(self.cursel.value)
#
#        popup = wnd.get_label('popup')
#        popup.destroy()
#        kaa.app.messagebar.set_message("")


def show_history(callback, words):

    doc = TextHistMode.build()
    dlg = kaa.app.show_dialog(doc)
    doc.mode.callback = callback
    doc.mode.set_candidates(words)
    doc.mode.set_query(dlg.get_label('editor'), '')

    dlg.on_console_resized()
    kaa.app.messagebar.set_message("Hit tab/shift+tab to select text. ")

    return dlg
