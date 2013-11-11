from kaa.command import Commands, command, norec, norerun
from kaa import document
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.keyboard import *

MoveSeparatorThemes = {
    'basic':
        Theme([
        ]),
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
    '\r': 'moveseparator.close',
    '\n': 'moveseparator.close',
}

class MoveSeparatorCommands(Commands):
    @command('moveseparator.prev')
    @norec
    @norerun
    def prev(self, wnd):
        if wnd.document.mode.target:
            wnd.document.mode.target.separator_prev()

    @command('moveseparator.next')
    @norec
    @norerun
    def next(self, wnd):
        if wnd.document.mode.target:
            wnd.document.mode.target.separator_next()

    @command('moveseparator.close')
    @norec
    @norerun
    def close(self, wnd):
        # restore cursor
        org_wnd = wnd.document.mode.org_wnd
        org_wnd.activate()

        # Destroy popup window
        popup = wnd.get_label('popup')
        if popup:
            popup.destroy()

        org_wnd.activate()

class MoveSeparatorMode(dialogmode.DialogMode):
    USE_UNDO = False

    @classmethod
    def build(cls, target):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)

        mode.org_wnd = target
        mode.target = target.splitter.parent

        f = dialogmode.FormBuilder(doc)
        f.append_text('caption', 'Hit cursor left/right key to resize window.')
        return doc

    def init_keybind(self):
        self.keybind.add_keybind(moveseparator_keys)

    def init_commands(self):
        super().init_commands()

        self.moveseparator_commands = MoveSeparatorCommands()
        self.register_command(self.moveseparator_commands)

    def init_themes(self):
        super().init_themes()
        self.themes.append(MoveSeparatorThemes)

    def is_cursor_visible(self):
        return 0   # hide cursor

    def on_esc_pressed(self, wnd, event):
        super().on_esc_pressed(wnd, event)
        self.moveseparator_commands.close(wnd)

    def on_str(self, wnd, s):
        pass

def move_separator(wnd):
    doc = MoveSeparatorMode.build(wnd)
    kaa.app.show_dialog(doc)

