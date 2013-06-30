import re, string
from kaa import cursor, keyboard
from kaa.filetype.default import modebase
from kaa.theme import Theme, Style

DialogTheme = Theme('default', [
    Style('default', 'default', 'default', False, False),
])

class DialogCursor(cursor.Cursor):
    def __init__(self, wnd, ranges):
        super().__init__(wnd)
        self.ranges = ranges

    def _findrange(self, curpos):
        for func  in self.ranges:
            f, t = func(self)
            if f <= curpos <= t:
                return f, t
        return self.ranges[0](self)

    def adjust_nextpos(self, curpos, nextpos):
        f, t = self._findrange(curpos)
        if nextpos >= t:
            return t
        if nextpos <= f:
            return f
        return nextpos

def _MarkRange(mark, cursor):
    return cursor.wnd.document.marks[mark]

def MarkRange(mark):
    return lambda cursor:_MarkRange(mark, cursor)

class DialogMode(modebase.ModeBase):
    autoshrink = False
    min_height = 1

    def init_theme(self):
        self.theme = DialogTheme

    def init_tokenizers(self):
        self.tokenizers = []

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.screen.build_entire_rows = True

    def calc_height(self, wnd):
        height = wnd.screen.get_total_height()
        w, h = wnd.getsize()
        maxw, maxh = wnd.mainframe.getsize()
        if height > maxh//2:
            return maxh//2
        elif height == h:
            return h
        elif height > h:
            return min(maxh//2, height)
        else:
            return max(self.min_height, height)

    def calc_position(self, wnd):
        w, h = wnd.getsize()
        height = self.calc_height(wnd)
        height = min(height, wnd.mainframe.height)

        top = wnd.mainframe.height - height -1 # todo: get height of messagebar
        return top, height

    def on_set_document(self, document):
        super().on_set_document(document)
        self.build_document()

    def on_start(self, wnd):
        pass

    def on_esc_pressed(self, wnd, event):
        pass

    def build_document(self):
        pass

    def on_document_updated(self, pos, inslen, dellen):
        super().on_document_updated(pos, inslen, dellen)

        if self.autoshrink:
            for wnd in self.document.wnds:
                w, h = wnd.getsize()
                top, newh = self.calc_position(wnd)
                # resize window if number of rows changed
                if newh != h:
                    wnd.get_label('popup').on_console_resized()
                    f, t = wnd.screen.get_visible_range()
                    if t == self.document.endpos():
                        # display as many rows as we can
                        wnd.screen.locate(t, bottom=True, align_always=True)
                        wnd.cursor.setpos(wnd.cursor.pos)

class FormBuilder:
    re_accel = re.compile(r'&.')
    def __init__(self, document):
        self.document = document

    def append_text(self, stylename, text, mark_start=None, mark_end=None, mark_pair=None,
                    on_shortcut=None, shortcut_style=None, shortcut_mark=None):

        # marks should not be moved until the document completed.
        self.document.marks.locked = True
        try:
            start = self.document.endpos()

            if shortcut_style is None:
                shortcut_style = stylename

            if stylename:
                style_id = self.document.mode.get_styleid(stylename)
            if shortcut_style:
                shortcut_style_id = self.document.mode.get_styleid(shortcut_style)

            # convert & escape to char and build shortcut dict
            lastpos = 0
            for m in self.re_accel.finditer(text):
                span = m.span()
                if span[0] != lastpos:
                    f = self.document.endpos()
                    self.document.append(text[lastpos:span[0]])
                    if stylename:
                        self.document.styles.setints(
                            f, self.document.endpos(), style_id)

                f = self.document.endpos()
                c = m.group()[1]
                if c != '&':
                    if on_shortcut:
                        self.document.mode.keybind.add_keybind(
                            {(keyboard.alt, c.lower()): on_shortcut})

                    if shortcut_mark:
                        self.document.marks[shortcut_mark] = f

                self.document.append(c)
                if shortcut_style:
                   self.document.styles.setints(f, f+1, shortcut_style_id)

                lastpos = m.end()

            else:
                if lastpos != len(text):
                    f = self.document.endpos()
                    self.document.append(text[lastpos:])
                    if stylename:
                        self.document.styles.setints(f, self.document.endpos(),
                                                 style_id)

            if mark_start is not None:
                self.document.marks[mark_start] = start

            if mark_end is not None:
                self.document.marks[mark_end] = self.document.endpos()

            if mark_pair is not None:
                self.document.marks[mark_pair] = (start, self.document.endpos())
        finally:
            self.document.marks.locked = False
