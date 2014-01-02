import kaa
from kaa import document, command
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style
from kaa.filetype.default import keybind
from kaa.commands import editorcommand
from kaa.keyboard import *

PasteLinesThemes = {
    'basic': [],
}

pastelines_keys = {
    (alt, '\r'): ('paste.lines'),
    (alt, '\n'): ('paste.lines'),
}


class PasteLinesMode(dialogmode.DialogMode):
    autoshrink = True
    USE_UNDO = True
    auto_indent = False

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
        pastelines_keys
    ]

    def init_themes(self):
        super().init_themes()
        self.themes.append(PasteLinesThemes)

    def close(self):
        super().close()
        self.target = None

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.set_cursor(dialogmode.DialogCursor(wnd,
                                               [dialogmode.MarkRange('pastetext')]))

        wnd.cursor.setpos(self.document.marks['pastetext'][0])

        kaa.app.messagebar.set_message("Paste text and hit alt+Enter")

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("Canceled")

    @command.commandid('paste.lines')
    @command.norec
    @command.norerun
    def paste_lines(self, w):
        f, t = self.document.marks['pastetext']
        s = self.document.gettext(f, t)

        self.target.document.mode.put_string(self.target, s)
        w.screen.selection.clear()

        kaa.app.messagebar.set_message("{} letters inserted".format(t - f))

        popup = w.get_label('popup')
        popup.destroy()

    @classmethod
    def build(cls, target):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)
        mode.target = target

        with dialogmode.FormBuilder(doc) as f:
            # caption
            f.append_text('caption',
                          'Paste text here. Hit alt+Enter when finished:')
            f.append_text('default', '\n')
            f.append_text('default', '', mark_pair='pastetext')

        return doc
