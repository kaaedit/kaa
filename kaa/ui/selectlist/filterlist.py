import kaa
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import selectlist

from kaa.theme import Theme, Style

from kaa.command import command, norec, norerun
from kaa.keyboard import *
from kaa.commands import editorcommand
import kaa.filetype.default.keybind


FilterListThemes = {
    'default':
        Theme([
            Style('default', 'default', 'Blue'),
            Style('caption', 'Red', 'Yellow'),
            Style('item', 'Yellow', 'Blue', nowrap=True),
            Style('item-active', 'Yellow', 'Red', nowrap=True),
        ])
}

class FilterListMode(selectlist.SelectItemList):
    SEP = '\n'
    def init_themes(self):
        super().init_themes()
        self.themes.append(FilterListThemes)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)
        wnd.set_label('filterlist', wnd)

    def set_candidates(self, candidates):
        self.candidates = candidates[:]

    def set_query(self, wnd, query):
        query = [f.upper() for f in query.split()]
        if query:
            items = []
            for s in self.candidates:
                u = s.upper()
                for q in query:
                    if q not in u:
                        break
                else:
                    items.append(s)
        else:
            items = self.candidates[:]

        items = [selectlist.SelectItem('item', s, s) for s in items]
        self.update_doc(items)
        if items:
            self.update_sel(wnd, items[0])


FilterListInputDlgThemes = {
    'default':
        Theme([
            Style('default', 'Red', 'Cyan'),
            Style('caption', 'Red', 'Yellow'),
        ])
}


filterlistinputdlg_keys = {
    down: 'filterlistdlg.next',
    up: 'filterlistdlg.prev',
    '\r': 'filterlistdlg.openfile',
    '\n': 'filterlistdlg.openfile',
}

class FilterListInputDlgMode(dialogmode.DialogMode):
    MAX_INPUT_HEIGHT = 4

    @classmethod
    def build(cls, caption, callback):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)

        mode.callback = callback

        f = dialogmode.FormBuilder(doc)
        f.append_text('caption', caption)
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='query')

        return doc

    def init_themes(self):
        super().init_themes()
        self.themes.append(FilterListInputDlgThemes)

    def init_keybind(self):
        self.keybind.add_keybind(kaa.filetype.default.keybind.edit_command_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.cursor_keys)
        self.keybind.add_keybind(kaa.filetype.default.keybind.emacs_keys)
        self.keybind.add_keybind(filterlistinputdlg_keys)

    def init_commands(self):
        super().init_commands()

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands )

        self.edit_commands = editorcommand.EditCommands()
        self.register_command(self.edit_commands)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.CURSOR_TO_MIDDLE_ON_SCROLL = False
        cursor = dialogmode.DialogCursor(wnd,
                   [dialogmode.MarkRange('query')])

        wnd.set_cursor(cursor)
        wnd.cursor.setpos(self.document.marks['query'][1])
        wnd.set_label('query_field', self)
        kaa.app.messagebar.set_message("Hit up/down to select item.")

    def calc_position(self, wnd):
        w, h = wnd.getsize()
        height = self.calc_height(wnd)
        height = min(height, self.MAX_INPUT_HEIGHT)
        top = wnd.mainframe.height - height - wnd.mainframe.MESSAGEBAR_HEIGHT
        return 0, top, wnd.mainframe.width, top+height

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("")
        self.callback(None)

    def on_edited(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.set_query(wnd, self.get_query())
        filterlist.get_label('popup').on_console_resized()

    def get_query(self):
        f, t = self.document.marks['query']
        return self.document.gettext(f, t)

    @command('filterlistdlg.next')
    @norec
    @norerun
    def next(self, wnd):

        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.sel_next(filterlist)

    @command('filterlistdlg.prev')
    @norec
    @norerun
    def prev(self, wnd):
        filterlist = wnd.get_label('filterlist')
        filterlist.document.mode.sel_prev(filterlist)

    @command('filterlistdlg.openfile')
    @norec
    @norerun
    def on_open(self, wnd):
        filterlist = wnd.get_label('filterlist')
        cur = filterlist.document.mode.cursel
        if cur:
            popup = wnd.get_label('popup')
            popup.destroy()

            self.callback(cur.value)



def show_listdlg(title, candidates, callback):
    doc = FilterListInputDlgMode.build(
            title, callback)
    dlg = kaa.app.show_dialog(doc)

    filterlistdoc = FilterListMode.build()
    dlg.add_doc('dlg_filterlist', 0, filterlistdoc)
    
    filterlistdoc.mode.set_candidates(candidates)

    list = dlg.get_label('dlg_filterlist')
    filterlistdoc.mode.set_query(list, '')
    dlg.on_console_resized()
    
    return dlg