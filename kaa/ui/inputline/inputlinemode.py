import kaa
from kaa import document, command
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.filetype.default import keybind
from kaa.commands import editorcommand
from kaa.keyboard import *

InputlineThemes = {
    'default':
        Theme([
            Style('caption', 'red', 'Green'),
        ])
}

inputline_keys = {
    ('\r'): ('inputline'),
    ('\n'): ('inputline'),
}

class InputlineMode(dialogmode.DialogMode):
    autoshrink = True
    USE_UNDO = True
    auto_indent = False

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
        inputline_keys
    ]

    def init_themes(self):
        super().init_themes()
        self.themes.append(InputlineThemes)

    def close(self):
        super().close()

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def init_commands(self):
        super().init_commands()

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands)

        self.edit_commands = editorcommand.EditCommands()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.set_cursor(dialogmode.DialogCursor(wnd,
                   [dialogmode.MarkRange('inputtext')]))

        wnd.cursor.setpos(self.document.marks['inputtext'][0])

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("Canceled")

    @command.command('inputline')
    def input_line(self, w):
        f, t = self.document.marks['inputtext']
        s = self.document.gettext(f, t)
        self.callback(w, s)

    @classmethod
    def build(cls, caption, callback):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)
        mode.callback = callback

        f = dialogmode.FormBuilder(doc)

        # caption
        f.append_text('caption', caption)
        f.append_text('default', ' ')
        f.append_text('default', '', mark_pair='inputtext')

        return doc

