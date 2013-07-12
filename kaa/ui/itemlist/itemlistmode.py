from kaa.command import Commands, command, norec
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.keyboard import *

ItemListTheme = Theme('default', [
    Style('default', 'default', 'Blue'),
    Style('caption', 'red', 'Blue'),
    Style('activemark', 'red', 'Green', nowrap=True),
    Style('nonactivemark', 'default', 'Blue', nowrap=True),
])

itemlist_keys = {
    left: 'itemlist.prev',
    right: 'itemlist.next',
    '\r': 'itemlist.close',
    '\n': 'itemlist.close',
}

class ItemListCommands(Commands):
    @command('itemlist.prev')
    def prev(self, wnd):
        mode = wnd.document.mode
        if mode.items:
            if mode.cursel is None:
                mode.cursel = 0
            elif mode.cursel > 0:
                mode.cursel -= 1

        wnd.document.mode._update_style(wnd)

    @command('itemlist.next')
    def next(self, wnd):
        mode = wnd.document.mode
        if mode.items:
            if mode.cursel is None:
                mode.cursel = 0
            elif mode.cursel < len(mode.items)-1:
                mode.cursel += 1

        wnd.document.mode._update_style(wnd)

    @command('itemlist.close')
    def close(self, wnd):
        callback = wnd.document.mode.callback
        cursel = wnd.document.mode.cursel

        # Destroy popup window
        popup = wnd.get_label('popup')
        if popup:
            popup.destroy()

        callback(cursel)

class ItemListMode(dialogmode.DialogMode):
    autoshrink = True

    @classmethod
    def build(cls, items, sel, callback):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)

        mode.items = items
        mode.cursel = sel
        mode.callback = callback

        f = dialogmode.FormBuilder(doc)
        for i, item in enumerate(items):
            f.append_text('default', item.replace('&', '&&'), mark_pair=i)
            f.append_text('default', ' ')

        mode._update_style(None)
        return doc

    def _update_style(self, wnd):
        cursor = None
        for i in range(len(self.items)):
            f, t = self.document.marks[i]
            if i == self.cursel:
                style = 'activemark'
            else:
                style = 'nonactivemark'
                cursor = f

            self.document.styles.setints(f, t, self.get_styleid(style))

        if wnd and cursor is not None:
            wnd.get_label('editor').cursor.setpos(cursor)

    def init_keybind(self):
        self.keybind.add_keybind(itemlist_keys)

    def init_commands(self):
        super().init_commands()

        self.itemlist_commands = ItemListCommands()
        self.register_command(self.itemlist_commands)

    def init_theme(self):
        self.theme = ItemListTheme

    def get_cursor_visibility(self):
        return 0   # hide cursor

    def on_esc_pressed(self, wnd, event):
        self.itemlist_commands.close(wnd)

    def on_str(self, wnd, s):
        pass
