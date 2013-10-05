import collections
from kaa import document
from kaa.ui.dialog import dialogmode


SelectItem = collections.namedtuple(
    'SelectItem', ['style', 'text', 'value'])

class SelectItemList(dialogmode.DialogMode):
    USE_UNDO = False
    items = ()
    cursel = None
    filterfunc = None
    caption = None

    @classmethod
    def build(cls):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)

        return doc

    def init_keybind(self):
        pass

    def get_cursor_visibility(self):
        return 0   # hide cursor

    def on_str(self, wnd, s):
        pass

    def calc_position(self, wnd):
        height = wnd.screen.get_total_height()
        height = min(height, wnd.mainframe.height//2)
        top = 0
        return 0, top, wnd.mainframe.width, top+height

    def update_doc(self, items):
        self.items = items

        with self.document.suspend_update():
            self.document.marks.clear()
            self.document.delete(0, self.document.endpos())
            f = dialogmode.FormBuilder(self.document)

            if self.caption:
                f.append_text('caption', self.caption+':\n')

            for item in self.items:
                f.append_text(item.style, item.text, mark_pair=item)
                f.append_text('default', ' ')

    def _update_item_style(self, wnd, item, activate, bottom=None):

        if item not in self.document.marks:
            return

        if activate:
            style = item.style+'-active'
        else:
            style = item.style

        f, t = self.document.marks[item]
        self.document.styles.setints(f, t, self.get_styleid(style))
        if activate:
            wnd.cursor.setpos(f, bottom=bottom)

    def update_sel(self, wnd, newsel, bottom=None):
        if self.cursel is not None:
            self._update_item_style(wnd, self.cursel, False)

        if newsel is not None:
            self._update_item_style(wnd, newsel, True, bottom=bottom)

        self.cursel = newsel

    def sel_next(self, wnd):
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
                if idx < len(self.items)-1:
                    newsel = self.items[idx+1]
                else:
                    newsel = self.items[0]

        self.update_sel(wnd, newsel)
        return newsel

    def sel_prev(self, wnd):
        bottom = None
        if not self.items:
            newsel = None
        elif self.cursel is None:
            newsel = self.items[-1]
            bottom = True
        else:
            try:
                idx = self.items.index(self.cursel)
            except ValueError:
                newsel = self.items[-1]
                bottom = True
            else:
                if idx > 0:
                    newsel = self.items[idx-1]
                else:
                    newsel = self.items[-1]
                    bottom = True
        self.update_sel(wnd, newsel, bottom=bottom)
        return newsel
