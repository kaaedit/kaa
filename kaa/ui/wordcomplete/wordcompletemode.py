import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist
from kaa.command import command, norec, norerun
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

        return items
    

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
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)
        mode.target = target
        
        f = dialogmode.FormBuilder(doc)
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
            top = max(0, cury-height)
        else:
            top = cury + 1

        return 0, top, wnd.mainframe.width, top+height

    @command('wordcomplete.select')
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
            
        wnd.document.mode.edit_commands.replace_string(
            self.target, self.wordpos[0], self.wordpos[1], 
            s, update_cursor=True)
        wnd.get_label('popup').destroy()
            
    def on_edited(self, wnd):
        super().on_edited(wnd)
        s = self.get_query()
        f, t = self.wordpos
        self.target.document.mode.edit_commands.replace_string(
            self.target, f, t, s, update_cursor=True)
        self.wordpos = (f, f+len(s))
        
    def on_esc_pressed(self, wnd, event):
        self.target.screen.selection.clear()
        super().on_esc_pressed(wnd, event)

    def start(self, list):
        self.orgpos = self.target.cursor.pos

        self.wordpos = (self.orgpos, self.orgpos)
        wnd = self.document.wnds[0]

        word = self.target.document.mode.get_word_at(self.orgpos)
        if word:
            f, t, cg = word
            if cg[0] in 'LMN': # Letter, Mark, Number
                self.wordpos = (f, t)
                
                s = self.target.document.gettext(f, t)
                if s:
                    self.target.screen.selection.set_range(f, t)
                    self.set_query(wnd, s)

        words = self.target.document.mode.get_word_list()
        words.extend(kaa.app.get_clipboards())


        list.document.mode.set_candidates(words)
        list.document.mode.candidates.sort(key=lambda v:v.text.upper())
        list.document.mode.set_query(list, self.get_query())
        list.get_label('popup').on_console_resized()

def show_wordlist(wnd):
    doc = WordCompleteInputMode.build(wnd)
    doc.mode.orgloc = wnd.get_cursor_loc()

    if doc.mode.orgloc[0] > (wnd.mainframe.height//2):
        doc.mode.stack_upper = True
    else:
        doc.mode.stack_upper = False

    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = WordCompleteList.build()
    filterlistdoc.mode.SEP = ' '
    list = dlg.add_doc('dlg_filterlist', 0, filterlistdoc)
    
    doc.mode.start(list)
    
    return dlg
