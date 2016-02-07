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
        return (max(0, l), max(0, b - 2))

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
                    kaa.app.set_focus(self.mainframe.popups[index - 1])
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
        super().on_focus()
        if self.parent and not self.parent.closed:
            self.parent.focused_child = self


class DialogWnd(_dialogwnd):

    def __init__(self, parent, doc, pos=None, border=False):
        self.border = border
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

        rc_input, rects = self.input.document.mode.resize_inputs(
            self.input, self.inputs)
        l, t, r, b = rc_input

        if rects:
            t = min(t, rects[0][1])
            b = max(b, rects[-1][3])

        if self.input.document.mode.border:
            l -= 1
            t -= 1
            r += 1
            b += 1

        self.set_rect(l, t, r, b)

        for w, (l, t, r, b) in zip(self.inputs, rects):
            w.set_rect(l, t, r, b)

        self.input.set_rect(*rc_input)

    def start(self):
        self.activate()
        self.input.document.mode.on_dialog_start(self.input)

    def add_doc(self, label, pos, doc):
        input = editor.TextEditorWindow(parent=self)
        self.set_label(label, input)
        input.show_doc(doc)
        self.inputs.insert(pos, input)
        return input

    def draw_screen(self):
        if self.input.document.mode.border:
            border_attr = self.input.document.mode.theme.get_style(
                'dialog-border').cui_colorattr

            self._cwnd.attron(border_attr)
            self._cwnd.border()
