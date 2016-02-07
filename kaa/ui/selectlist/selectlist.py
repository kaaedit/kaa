import collections
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.keyboard import *
from kaa.command import commandid, norec, norerun


SelectItem = collections.namedtuple(
    'SelectItem', ['style', 'activestyle', 'text', 'value'])

selectlist_keys = {
    down: 'selectitemlist.next',
    (ctrl, 'n'): 'selectitemlist.next',
    (ctrl, 'f'): 'selectitemlist.next',
    tab: 'selectitemlist.next',
    up: 'selectitemlist.prev',
    (ctrl, 'p'): 'selectitemlist.prev',
    (ctrl, 'b'): 'selectitemlist.prev',
    (shift, tab): 'selectitemlist.prev',
}


class SelectItemList(dialogmode.DialogMode):
    USE_UNDO = False
    NO_WRAPINDENT = False
    CAPTION_STYLE = 'caption'
    items = ()
    cursel = None
    filterfunc = None
    caption = None
    SEP = ' '

    @classmethod
    def build(cls):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)

        return doc

    def is_cursor_visible(self):
        return 0   # hide cursor

    def init_keybind(self):
        super().init_keybind()
        self.keybind.add_keybind(selectlist_keys)

    def on_str(self, wnd, s, overwrite=False):
        pass

    def calc_height(self, wnd):
        height = wnd.screen.get_total_height(wnd.mainframe.height // 2)
        return height

    def update_doc(self, items):
        self.items = list(collections.OrderedDict((i, 1)
                                                  for i in items).keys())

        self.cursel = None

        self.document.marks.clear()
        self.document.delete(0, self.document.endpos())
        with dialogmode.FormBuilder(self.document) as f:
            if self.caption:
                f.append_text(self.CAPTION_STYLE, self.caption + ':\n')

            for n, item in enumerate(self.items):
                f.append_text(item.style, item.text, mark_pair=item)
                if n != (len(self.items) - 1):
                    f.append_text('default', self.SEP)

    def _update_item_style(
            self, wnd, item, activate, middle=None, bottom=None):

        if item not in self.document.marks:
            return

        if activate:
            style = item.activestyle
        else:
            style = item.style

        f, t = self.document.marks[item]
        self.document.setstyles(f, t, self.get_styleid(style))
        if activate:
            wnd.screen.apply_updates()
            top = not middle and not bottom
            wnd.screen.locate(f, top=top, middle=middle, bottom=bottom)
            wnd.update_window()

    def update_sel(self, wnd, newsel, middle=None, bottom=None):
        if self.cursel is not None:
            self._update_item_style(wnd, self.cursel, False)

        if newsel is not None:
            self._update_item_style(wnd, newsel, True,
                                    middle=middle, bottom=bottom)

        self.cursel = newsel

    @commandid('selectitemlist.next')
    @norec
    @norerun
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
                if idx < len(self.items) - 1:
                    newsel = self.items[idx + 1]
                else:
                    newsel = self.items[0]

        self.update_sel(wnd, newsel, bottom=True)
        return newsel

    @commandid('selectitemlist.prev')
    @norec
    @norerun
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
                    newsel = self.items[idx - 1]
                else:
                    newsel = self.items[-1]
                    bottom = True

        self.update_sel(wnd, newsel, bottom=bottom)
        return newsel
