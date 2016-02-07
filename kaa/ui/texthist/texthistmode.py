import kaa
from kaa.ui.selectlist import selectlist, filterlist
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


def show_history(title, callback, words):
    doc = filterlist.FilterListInputDlgMode.build(
        title, callback)
    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = TextHistMode.build()
    list = dlg.add_doc('dlg_filterlist', 0, filterlistdoc)

    filterlistdoc.mode.set_candidates(words)
    filterlistdoc.mode.set_query(list, '')
    dlg.on_console_resized()

    return dlg
