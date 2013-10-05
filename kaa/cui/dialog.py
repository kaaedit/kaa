import kaa
from . import wnd, editor

class _dialogwnd(wnd.Window, kaa.context.ContextRoot):
    focused_child = None
    def __init__(self, parent, pos=None):

        if pos is None:
            # specify default position to avoid flicker
            pos = self._get_defaultpos(parent)
        super().__init__(parent, pos=pos)

        self.set_label('popup', self)

    def _get_defaultpos(self, parent):
        if not parent:
            parent = self.mainframe
        l, t, r, b = parent.rect
        return (max(0, l), max(0, b-2))

    def destroy(self):
        # Am I a active dialog?
        update_focus = kaa.app.focus in self.walk_children()
        super().destroy()

        # update focus
        if update_focus:
            kaa.app.set_focus(None)

        try:
            index = self.mainframe.popups.index(self)
        except ValueError:
            pass
        else:
            del self.mainframe.popups[index]
            if update_focus:
                if index > 0:
                    kaa.app.set_focus(self.mainframe.popups[index-1])
                elif not self.mainframe.closed:
                    kaa.app.set_focus(self.mainframe)

        self.destroy_context()

        # If this dialog was inputline window, resize entire screen now.
        if self.mainframe.inputline is self:
            self.mainframe.inputline = None
            self.mainframe.on_console_resized()

    def draw_screen(self):
        pass

    def on_focus(self):
        """Got focus"""
        if self.parent and not self.parent.closed:
            self.parent.focused_child = self

class DialogWnd(_dialogwnd):
    def __init__(self, parent, doc, pos=None):
        super().__init__(parent, pos)
        self.inputs = []
        self.input = editor.TextEditorWindow(parent=self)
        self.set_label('editor', self.input)
        self.input.show_doc(doc)

    def destroy(self):
        self.input = None
        self.inputs = []
        super().destroy()

    def activate(self):
        for input in self.inputs:
            input.bring_top()
        super().activate()

    def on_focus(self):
        super().on_focus()
        if self.focused_child and not self.focused_child.closed:
            self.focused_child.activate()
        else:
            self.input.activate()

    def on_console_resized(self):
        """Resize wnds"""

        rects = [w.document.mode.calc_position(w) for w in self.inputs]
        heights = [b-t for (l, t, r, b) in rects]

        rc_input = self.input.document.mode.calc_position(self.input)

        l, t, r, b = rc_input
        t = t - sum(heights)
        self.set_rect(l, t, r, b)

        for w, (wl, wt, wr, wb) in zip(self.inputs, rects):
            b = t + (wb - wt)
            w.set_rect(l, t, r, b)
            t = b + 1

        self.input.set_rect(*rc_input)

    def start(self):
        self.activate()
        self.input.document.mode.on_start(self.input)

    def add_doc(self, label, pos, doc):
        input = editor.TextEditorWindow(parent=self)
        self.set_label('label', input)
        input.show_doc(doc)
        self.inputs.insert(pos, input)

