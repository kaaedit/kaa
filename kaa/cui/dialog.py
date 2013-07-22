import kaa
from . import wnd, editor

class DialogWnd(wnd.Window, kaa.context.ContextRoot):
    def __init__(self, parent, doc, pos=None):

        if pos is None:
            # specify default position to avoid flicker
            pos = self._get_defaultpos(parent)
        super().__init__(parent, pos=pos)

        self.set_label('popup', self)
        self.document = doc
        self.input = editor.TextEditorWindow(parent=self, pos=pos)
        self.input.show_doc(doc)
        self.set_label('editor', self.input)

    def _get_defaultpos(self, parent):
        if not parent:
            parent = self.mainframe
        l, t, r, b = parent.rect
        return (max(1,l), max(1, b-2))

    def destroy(self):

        # Am I a active dialog?
        update_focus = kaa.app.focus in self.walk_children()
        super().destroy()

        self.document = self.input = None

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

        if self.mainframe.inputline is self:
            self.mainframe.inputline = None
            self.mainframe.on_console_resized()


    def activate(self):
        super().activate()
        self.input.activate()

    def on_focus(self):
        self.input.activate()

    def on_console_resized(self):
        """Resize wnds"""

        l, t, r, b = self.document.mode.calc_position(self.input)

        self.set_rect(l, t, r, b)
        self.input.set_rect(l, t, r, b)

    def draw_screen(self):
        pass

    def update_window(self):
        self.draw_screen()
        self.input.refresh()

    def start(self):
        self.input.activate()
        self.document.mode.on_start(self.input)

