import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist, selectlist
from kaa.command import command, norec, norerun
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
        if query:
            query = query.upper().split()
            matches = self.candidates[:]
            for i, s in enumerate(self.candidates):
                u = s.value.name.upper()
                for q in query:
                    if q not in u:
                        matches[i] = False
                        break

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

        return items

    def update_doc(self, items):
        self.items = list(items)
        self.cursel = None

        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())
        f = dialogmode.FormBuilder(self.document)

        parents = ()
        for n, item in enumerate(self.items):
            if item.value.token == 'namespace':
                parents = item.value.parents+(item.value,)
                if n != 0:
                    f.append_text('default', '\n'+'  '*len(item.value.parents))
                
                f.append_text(item.style, item.text, mark_pair=item)
                f.append_text('default', '\n'+'  '*len(parents))
            else:
                if parents != item.value.parents:
                    f.append_text('default', 
                                  '\n'+'  '*(len(item.value.parents)))
                    parents = item.value.parents

                f.append_text(item.style, item.text, mark_pair=item)
                f.append_text('default', ' ')




toclistdlg_keys = {
    tab: 'filterlistdlg.next',
    (shift, tab): 'filterlistdlg.prev',
}


class TOCListInputDlgMode(filterlist.FilterListInputDlgMode):
    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(toclistdlg_keys)

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
    
    return dlg
