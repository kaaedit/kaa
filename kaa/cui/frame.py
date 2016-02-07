import curses

import kaa
import kaa.context
from kaa.cui.wnd import Window
from kaa.cui import splitter, editor


class ChildFrame(Window, kaa.context.ContextRoot):
    splitter = None
    active_editor = None

    def __init__(self, parent, pos=None):
        super().__init__(parent, pos=pos)

        self.set_label('frame', self)
        self.splitter = None

    def destroy(self):
        if self.splitter:
            self.splitter.destroy()

        super().destroy()

        self.destroy_context()
        self.mainframe.childframes.remove(self)

    def show_doc(self, doc):
        if self.splitter:
            self.splitter.destroy()
            self.splitter = None

        editorwnd = editor.TextEditorWindow(parent=self)
        editorwnd.show_doc(doc)
        self.splitter = splitter.Splitter(self, None, editorwnd)
        self.splitter.set_rect(*self.rect)
        return editorwnd

    def set_active_editor(self, editorwnd):
        self.active_editor = editorwnd

    def get_documents(self):
        docs = []
        for splitter, w in self.splitter.walk():
            if w:
                doc = w.document
                if doc not in docs:
                    docs.append(doc)
        return docs

    def get_title(self):
        if self.splitter:
            return '/'.join(self.splitter.get_title())
        return '<untitled>'

    def get_editors(self):
        if self.splitter:
            return self.splitter.get_editors()
        else:
            return []

    def bring_top(self):
        super().bring_top()
        if self.splitter:
            self.splitter.bring_top()
        self.mainframe.set_activeframe(self)
        self.mainframe.on_console_resized()

    def on_setrect(self, l, t, r, b):
        if self.splitter:
            self.splitter.set_rect(l, t, r, b)

    def on_focus(self):
        super().on_focus()
        self.mainframe.set_activeframe(self)

        if self.active_editor:
            self.active_editor.activate()
        elif self.splitter:
            self.splitter.activate()
        else:
            kaa.app.set_focus(self)

    def draw_screen(self):
        if kaa.app.get_activeframe() is not self:
            return

        if self.splitter:
            self.splitter.draw()


class MainFrame(Window, kaa.context.ContextRoot):

    """The main frame of application

    Attributes:
        editorwnd -- current editor wnd
    """

    popups = []
    inputline = None

    need_refresh = False
#    need_redraw = False
    childframes = []
    activeframe = None

    MESSAGEBAR_HEIGHT = 1
    BORDER_WIDTH = 1

    def __init__(self, wnd):
        Window.mainframe = self
        super().__init__(None, wnd)
        self.width, self.height = 0, 0

        self.messagebar = editor.TextEditorWindow(parent=self)

    def destroy(self):
        super().destroy()
        self.childframes = None
        self.activeframe = None
        self.destroy_context()

    def set_messagebar(self, doc):
        self.messagebar.show_doc(doc)

    def on_focus(self):
        super().on_focus()
        if self.activeframe:
            self.activeframe.on_focus()

    def on_console_resized(self):
        """Resize wnds"""
        self.height, self.width = self._cwnd.getmaxyx()
        self.messagebar.set_rect(
            0, self.height - self.MESSAGEBAR_HEIGHT, self.width, self.height)

        if self.inputline and not self.inputline.closed:
            w, h = self.inputline.getsize()
            editorheight = max(1, self.height - h - self.MESSAGEBAR_HEIGHT)
        else:
            editorheight = max(1, self.height - self.MESSAGEBAR_HEIGHT)

        if self.activeframe:
            self.activeframe.set_rect(0, 0, self.width, editorheight)

        for popup in self.popups:
            popup.on_console_resized()

    def _get_temporary_frame(self):
        # if kaa has only one frame and the frame has temporary document,
        # then dispose the document and reuse the frame.

        frames = kaa.app.get_frames()
        if len(frames) != 1:
            return

        wnd = frames[0].splitter.wnd
        if wnd and wnd.document:
            doc = wnd.document
            if doc.temporary and not wnd.document.undo.is_dirty():
                if len(doc.wnds) == 1:
                    return frames[0]

    def register_childframe(self, childframe):
        if childframe in self.childframes:
            self.childframes.remove(childframe)
        self.childframes.insert(0, childframe)

    def is_idle(self):
        return not self.popups and not self.inputline

    def show_doc(self, doc):
        frame = self._get_temporary_frame()
        if frame:
            if frame.splitter.wnd.document is doc:
                return
        else:
            frame = ChildFrame(parent=self)

        editorwnd = frame.show_doc(doc)
        editorwnd.activate()

        self.register_childframe(frame)

        self.set_activeframe(frame)
        self.on_console_resized()

        return editorwnd

    def set_activeframe(self, frame):
        self.activeframe = frame

    def add_popup(self, popup):
        self.popups.append(popup)

    def show_inputline(self, inputline):
        self.inputline = inputline
        self.show_dialog(inputline)
        self.on_console_resized()

    def show_dialog(self, dialog):
        self.add_popup(dialog)
        dialog.on_console_resized()
        dialog.start()

    def request_refresh(self):
        self.need_refresh = True

    def run_refresh(self):
        if self.need_refresh:
            #            if self.need_redraw:
            #                for child in self.walk_children():
            #                    child._cwnd.touchwin()

            curses.panel.update_panels()
            curses.doupdate()
            self.need_refresh = False
#            self.need_refresh = self.need_redraw = False

            return True

    def on_idle(self):
        if not self.closed:
            if self.run_refresh():
                return True

            for child in self.walk_children():
                if not child.closed:
                    if child.on_idle():
                        return True

            for child in self.walk_children():
                if not child.closed:
                    child.update_window()
