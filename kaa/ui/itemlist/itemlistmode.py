from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.keyboard import *

ItemListThemes = {
    'basic': [],
}

itemlist_keys = {
    left: 'itemlist.prev',
    (ctrl, 'p'): 'itemlist.prev',
    (ctrl, 'b'): 'itemlist.prev',
    (shift, tab): 'itemlist.prev',
    right: 'itemlist.next',
    (ctrl, 'n'): 'itemlist.next',
    (ctrl, 'f'): 'itemlist.next',
    tab: 'itemlist.next',
    '\r': 'itemlist.selected',
    '\n': 'itemlist.selected',
}


class ItemListMode(dialogmode.DialogMode):
    border = True
    autoshrink = True
    CAPTIONSEP = '\n'
    ITEMSEP = ' '

    @classmethod
    def build(cls, caption, items, sel, callback, onchange=None):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)

        mode.items = items
        mode.cursel = sel
        mode.callback = callback
        mode.onchange = onchange

        with dialogmode.FormBuilder(doc) as f:

            if caption:
                f.append_text('caption', caption.replace('&', '&&'))
                f.append_text('default', cls.CAPTIONSEP)

            for i, item in enumerate(items):
                f.append_text('default', item.replace('&', '&&'), mark_pair=i)
                f.append_text('default', cls.ITEMSEP)

            mode._update_style(None)
        return doc

    def _update_style(self, wnd):
        cursor = None
        for i in range(len(self.items)):
            f, t = self.document.marks[i]
            if i == self.cursel:
                style = 'activemark'
                cursor = f
            else:
                style = 'nonactivemark'
                if cursor is None:
                    cursor = f

            self.document.setstyles(f, t, self.get_styleid(style))

        if wnd and cursor is not None:
            wnd.get_label('editor').cursor.setpos(cursor)

    def init_keybind(self):
        self.keybind.add_keybind(itemlist_keys)

    def init_themes(self):
        super().init_themes()
        self.themes.append(ItemListThemes)

    def is_cursor_visible(self):
        return 0   # hide cursor

    def on_esc_pressed(self, wnd, event):
        self.cursel = None
        self.selected(wnd)

    def on_str(self, wnd, s, overwrite=False):
        cursel = self.cursel
        if cursel is None:
            cursel = -1
        c = s[-1]
        c = (c.lower(), c.upper())
        cont = True
        while cont:
            if cursel < 0:
                cont = False
            for i in range(cursel + 1, len(self.items)):
                if self.items[i].startswith(c):
                    self.cursel = i
                    self._update_style(wnd)
                    return
            cursel = -1

    @commandid('itemlist.prev')
    @norec
    @norerun
    def prev(self, wnd):
        mode = wnd.document.mode
        if mode.items:
            cur = mode.cursel
            if mode.cursel is None:
                mode.cursel = 0
            elif mode.cursel > 0:
                mode.cursel -= 1

            if cur is None or cur != mode.cursel:
                if mode.onchange:
                    mode.onchange(mode.cursel)

        wnd.document.mode._update_style(wnd)

    @commandid('itemlist.next')
    @norec
    @norerun
    def next(self, wnd):
        mode = wnd.document.mode
        if mode.items:
            cur = mode.cursel
            if mode.cursel is None:
                mode.cursel = 0
            elif mode.cursel < len(mode.items) - 1:
                mode.cursel += 1

            if cur is None or cur != mode.cursel:
                if mode.onchange:
                    mode.onchange(mode.cursel)

        wnd.document.mode._update_style(wnd)

    @commandid('itemlist.selected')
    @norec
    @norerun
    def selected(self, wnd):
        callback = wnd.document.mode.callback
        cursel = wnd.document.mode.cursel

        # Destroy popup window
        popup = wnd.get_label('popup')
        if popup:
            popup.destroy()

        callback(cursel)
