from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.keyboard import *

MoveSeparatorThemes = {
    'basic': [],
}

moveseparator_keys = {
    left: 'moveseparator.prev',
    up: 'moveseparator.prev',
    (ctrl, 'p'): 'moveseparator.prev',
    (ctrl, 'b'): 'moveseparator.prev',
    right: 'moveseparator.next',
    down: 'moveseparator.next',
    (ctrl, 'f'): 'moveseparator.next',
    (ctrl, 'n'): 'moveseparator.next',
    '\r': 'moveseparator.done',
    '\n': 'moveseparator.done',
}


class MoveSeparatorMode(dialogmode.DialogMode):
    USE_UNDO = False

    @classmethod
    def build(cls, target):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)

        mode.org_wnd = target
        mode.target = target.splitter.parent

        with dialogmode.FormBuilder(doc) as f:
            f.append_text('caption',
                          'Hit cursor left/right key to resize window.')
        return doc

    def init_keybind(self):
        self.keybind.add_keybind(moveseparator_keys)

    def init_themes(self):
        super().init_themes()
        self.themes.append(MoveSeparatorThemes)

    def is_cursor_visible(self):
        return 0   # hide cursor

    def on_esc_pressed(self, wnd, event):
        self.done(wnd)

    def on_str(self, wnd, s, overwrite=False):
        pass

    @commandid('moveseparator.prev')
    @norec
    @norerun
    def prev(self, wnd):
        if wnd.document.mode.target:
            wnd.document.mode.target.separator_prev()

    @commandid('moveseparator.next')
    @norec
    @norerun
    def next(self, wnd):
        if wnd.document.mode.target:
            wnd.document.mode.target.separator_next()

    @commandid('moveseparator.done')
    @norec
    @norerun
    def done(self, wnd):
        # restore cursor
        org_wnd = wnd.document.mode.org_wnd
        org_wnd.activate()

        # Destroy popup window
        popup = wnd.get_label('popup')
        if popup:
            popup.destroy()

        org_wnd.activate()


def move_separator(wnd):
    doc = MoveSeparatorMode.build(wnd)
    kaa.app.show_dialog(doc)
