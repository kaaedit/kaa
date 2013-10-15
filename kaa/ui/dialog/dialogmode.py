import re, string
from kaa import cursor, keyboard
from kaa.filetype.default import modebase
from kaa.theme import Theme, Style

DialogThemes = {
    'default':
        Theme([
            Style('default', 'default', 'default', False, False),
    ])
}

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
    NO_WRAPINDENT = False
    autoshrink = False
    min_height = 1

    def init_themes(self):
        super().init_themes()
        self.themes.append(DialogThemes)

    def init_tokenizers(self):
        self.tokenizers = []

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.screen.build_entire_rows = True # todo: use mode.

    def calc_width(self, wnd):
        return wnd.mainframe.getsize()[0]

    def calc_height(self, wnd):
        height = wnd.screen.get_total_height()
        if height < self.min_height:
            return self.min_height
        maxw, maxh = wnd.mainframe.getsize()
        return min(maxh, height)

    def calc_position(self, wnd):
        w = self.calc_width(wnd)
        wnd.screen.setsize(w, wnd.screen.height)
        height = self.calc_height(wnd)
        height = min(height, wnd.mainframe.messagebar.rect[1])

        top = wnd.mainframe.messagebar.rect[1] - height

        return 0, top, wnd.mainframe.width, top+height

    def on_start(self, wnd):
        pass

    def on_esc_pressed(self, wnd, event):
        pass

    def on_document_updated(self, pos, inslen, dellen):
        super().on_document_updated(pos, inslen, dellen)

        if self.autoshrink:
            for wnd in self.document.wnds:
                w, h = wnd.getsize()
                l, t, r, b = self.calc_position(wnd)
                newh = b - t
                # resize window if number of rows changed
                if newh != h:
                    wnd.get_label('popup').on_console_resized()
                    wnd.mainframe.on_console_resized()
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
                    on_shortcut=None, shortcut_style=None, shortcut_mark=None,
                    shortcut_need_alt=True):

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
                        if not shortcut_need_alt:
                            self.document.mode.keybind.add_keybind(
                                {(c.lower()): on_shortcut})
                            self.document.mode.keybind.add_keybind(
                                {(c.upper()): on_shortcut})

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

            # Dialog texts are not undoable
            if self.document.undo:
                self.document.undo.clear()

        finally:
            self.document.marks.locked = False

