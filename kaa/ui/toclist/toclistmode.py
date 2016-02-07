import kaa
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist, selectlist
from kaa.command import commandid, norec, norerun
from kaa.keyboard import *


class TOCList(filterlist.FilterListMode):
    MAX_CAPTION_LEN = 30
    USE_PHRASE_STYLE = True

    def set_candidates(self, candidates):
        self.candidates = [
            selectlist.SelectItem(
                'selectitem' if c.token != 'namespace' else 'selectitem2', 'selectitem-active', c.dispname, c)
            for c in candidates]

    def _filter_items(self, query):
        first = None
        if query:
            query = query.upper().split()
            matches = self.candidates[:]
            for i, s in enumerate(self.candidates):
                u = s.value.name.upper()
                for q in query:
                    if q not in u:
                        matches[i] = False
                        break
                    if not first:
                        first = s

            ns = None
            for i in range(len(self.candidates)):
                if self.candidates[i].value.token == 'namespace':
                    ns = i
                else:
                    if matches[i] and ns is not None:
                        matches[ns] = self.candidates[ns]
            items = [m for m in matches if m]
        else:
            items = self.candidates[:]
            first = items[0] if items else None

        return first, items

    def update_doc(self, items):
        self.items = list(items)
        self.cursel = None

        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())
        with dialogmode.FormBuilder(self.document) as f:
            prev = None
            for item in self.items:
                if item.value.token == 'namespace':
                    if prev:
                        f.append_text('default',
                                      '\n' + '  ' * len(item.value.get_parents()))
                    f.append_text(item.style, item.text, mark_pair=item)

                else:
                    if prev and (prev.value.token == 'namespace' or
                                 prev.value.get_parents() != item.value.get_parents()):

                        f.append_text('default',
                                      '\n' + '  ' * (len(item.value.get_parents())))

                    f.append_text(item.style, item.text, mark_pair=item)
                    f.append_text('default', ' ')

                prev = item

    def sel_next_namespace(self, wnd):
        if not self.items:
            newsel = None
        elif self.cursel is None:
            newsel = self.items[0]
        else:
            try:
                idx = self.items.index(self.cursel)
            except ValueError:
                newsel = self.items[0]
            else:
                idx += 1
                while idx < len(self.items):
                    newsel = self.items[idx]
                    if newsel.value.token == 'namespace':
                        break
                    idx += 1
                else:
                    newsel = self.items[0]

        self.update_sel(wnd, newsel, bottom=True)
        return newsel

    def sel_prev_namespace(self, wnd):
        bottom = None
        if not self.items:
            newsel = None
        elif self.cursel is None:
            newsel = self.items[-1]
            bottom = True
        else:
            newsel = None
            for i, item in enumerate(self.items):
                if item is self.cursel:
                    bottom = True
                    if newsel:
                        break
                    newsel = None

                if item.value.token == 'namespace':
                    newsel = item

            if not newsel:
                newsel = self.items[-1]

        self.update_sel(wnd, newsel, bottom=bottom)
        return newsel


toclistdlg_keys = {
    tab: 'filterlistdlg.next',
    (shift, tab): 'filterlistdlg.prev',
    (alt, 'p'): 'toclistdlg.prev_namespace',
    (alt, 'n'): 'toclistdlg.next_namespace',
}


class TOCListInputDlgMode(filterlist.FilterListInputDlgMode):

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(toclistdlg_keys)

    @commandid('toclistdlg.next_namespace')
    @norec
    @norerun
    def sel_next_namespace(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.sel_next_namespace(filterlist)

    @commandid('toclistdlg.prev_namespace')
    @norec
    @norerun
    def sel_prev_namespace(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.sel_prev_namespace(filterlist)


def show_toclist(wnd, toclist):
    def callback(result):
        if result:
            wnd.cursor.setpos(result.pos)

    doc = TOCListInputDlgMode.build(
        'Search:', callback)
    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = TOCList.build()
    list = dlg.add_doc('dlg_filterlist', 0, filterlistdoc)

    filterlistdoc.mode.set_candidates(toclist)
    filterlistdoc.mode.set_query(list, '')
    dlg.on_console_resized()

    pos = wnd.cursor.pos
    last = None
    for item in filterlistdoc.mode.candidates:
        if pos < item.value.pos:
            break
        last = item

    if last:
        filterlistdoc.mode.update_sel(list, last, bottom=True)

    return dlg
