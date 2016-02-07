import curses
import collections
import kaa
from kaa import document
from kaa.ui.statusbar import statusbarmode
from kaa.cui import editor


class Splitter:
    vsep = hsep = 0

    def __init__(self, frame, parent, wnd):
        super().__init__()

        self.wnd = self.left = self.right = self.above = self.below = None
        assert frame
        self.frame = frame
        self.parent = parent
        self.wnd = wnd
        self.wnd.set_splitter(self)
        self.statusbar = None
        self.rect = (0, 0, 0, 0)

    def walk(self):
        stack = collections.deque([self])
        while stack:
            v = stack.pop()
            yield (v, v.wnd)
            if v.left:
                stack.append(v.right)
                stack.append(v.left)
            elif v.above:
                stack.append(v.below)
                stack.append(v.above)

    def activate(self):
        if self.wnd:
            self.wnd.activate()
        elif self.left:
            self.left.activate()
            self.right.activate()
        elif self.above:
            self.above.activate()
            self.below.activate()

    def set_rect(self, l, t, r, b):
        self.rect = (l, t, r, b)
        self.resize()

    def _destroy_children(self):
        if self.left:
            self.left.destroy()
        if self.right:
            self.right.destroy()
        if self.above:
            self.above.destroy()
        if self.below:
            self.below.destroy()
        self.left = self.right = self.above = self.below = None

    def destroy(self):
        self._destroy_children()
        if self.wnd:
            self.wnd.destroy()
        if self.statusbar:
            self.statusbar.destroy()

        self.parent = None
        self.frame = None
        self.statusbar = None

    def get_buddy(self):
        if self.parent:
            if self.parent.left is self:
                return self.parent.right
            elif self.parent.right is self:
                return self.parent.left
            elif self.parent.above is self:
                return self.parent.below
            elif self.parent.below is self:
                return self.parent.above

    def show_doc(self, doc):
        if not self.wnd:
            self._destroy_children()
            self.wnd = editor.TextEditorWindow(parent=self.frame)
            self.resize()

        self.wnd.show_doc(doc)

    def split(self, vert, doc=None):
        w, h = self.wnd.getsize()
        if not doc:
            doc = self.wnd.document
        if vert:
            self.vsep = w // 2 + 1
            self.left = Splitter(self.frame, self, self.wnd)
            self.right = Splitter(self.frame, self, self.wnd.dup())
            self.right.wnd.show_doc(doc)
            self.wnd = None
            self.left.activate()
            ret = self.right
        else:
            self.hsep = h // 2 + 1
            self.above = Splitter(self.frame, self, self.wnd)
            self.below = Splitter(self.frame, self, self.wnd.dup())
            self.below.wnd.show_doc(doc)
            self.wnd = None
            self.above.activate()
            ret = self.below

        self.resize()
        return ret

    def join(self, wnd):
        if self.wnd:
            # not splitted
            return

        next = None
        for w in (self.left, self.right, self.above, self.below):
            if w:
                if wnd is next is None:
                    # Keep first window if wnd is None
                    next = w
                elif wnd is not w.wnd:
                    w.destroy()
                else:
                    next = w

        # chain child splitter to parent
        next.parent = self.parent
        next.rect = self.rect
        if self.frame.splitter is self:
            self.frame.splitter = next
        else:
            if self.parent.left is self:
                self.parent.left = next
            elif self.parent.right is self:
                self.parent.right = next
            elif self.parent.above is self:
                self.parent.above = next
            elif self.parent.below is self:
                self.parent.below = next

        # clean up
        self.left = self.right = self.above = self.below = None
        self.destroy()

        next.resize()
        next.activate()

    def _build_statusbar(self):
        self.statusbar = editor.TextEditorWindow(parent=self.frame)

        doc = document.Document()
        mode = statusbarmode.StatusBarMode()
        doc.setmode(mode)
        self.statusbar.show_doc(doc)

    def resize(self):
        l, t, r, b = self.rect
        if self.wnd:
            if not self.statusbar:
                self._build_statusbar()
            self.statusbar.set_rect(l, b - 1, r, b)
            self.statusbar.bring_top()
            self.wnd.set_rect(l, t, r, b - 1)
            self.wnd.set_statusbar(self.statusbar.document.mode)
            self.wnd.bring_top()
        else:
            if self.statusbar:
                self.statusbar.destroy()
                self.statusbar = None

            if self.left:
                self.left.set_rect(l, t, l + self.vsep, b)
                self.right.set_rect(l + self.vsep + 1, t, r, b)
            elif self.above:
                self.above.set_rect(l, t, r, t + self.hsep)
                self.below.set_rect(l, t + self.hsep, r, b)

    def get_editors(self):
        if self.wnd:
            return [self.wnd]
        elif self.left:
            return self.left.get_editors() + self.right.get_editors()
        else:
            return self.above.get_editors() + self.below.get_editors()

    def get_title(self):
        if self.wnd:
            doc = self.wnd.document
            return [doc.get_title()]

        elif self.left:
            return self.left.get_title() + self.right.get_title()

        else:
            return self.above.get_title() + self.below.get_title()

    def bring_top(self):
        if self.wnd:
            if self.statusbar:
                self.statusbar.bring_top()
            self.wnd.bring_top()

        elif self.left:
            self.left.bring_top()
            self.right.bring_top()

        else:
            self.above.bring_top()
            self.below.bring_top()

    def draw(self):
        self.frame._cwnd.attron(
            kaa.app.colors.get_color(
                kaa.app.colors.colornames.get('CYAN'),
                kaa.app.colors.colornames.get('DEFAULT')))
        l, t, r, b = self.rect
        if self.left:
            try:
                self.frame._cwnd.vline(
                    t, l + self.vsep, curses.ACS_VLINE, b - t)
            except curses.error:
                pass

            self.left.draw()
            self.right.draw()
        elif self.above:
            self.above.draw()
            self.below.draw()

    def separator_prev(self):
        if self.left:
            if self.vsep > 3:
                self.vsep -= 1
                self.resize()
                self.draw()
        elif self.above:
            if self.hsep > 3:
                self.hsep -= 1
                self.resize()
                self.draw()

    def separator_next(self):
        l, t, r, b = self.rect

        if self.left:
            if r - (l + self.vsep) > 4:
                self.vsep += 1
                self.resize()
                self.draw()
        elif self.above:
            if b - (t + self.hsep) > 3:
                self.hsep += 1
                self.resize()
                self.draw()
