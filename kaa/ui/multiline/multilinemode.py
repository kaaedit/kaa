import kaa
from kaa import document, command
from kaa.ui.dialog import dialogmode
from kaa.filetype.default import keybind
from kaa.keyboard import *

multiline_keys = {
    (alt, '\r'): ('multiline.done'),
    (alt, '\n'): ('multiline.done'),
}


class MultilineMode(dialogmode.DialogMode):
    autoshrink = True
    USE_UNDO = True
    auto_indent = False

    callback = None

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
        multiline_keys
    ]

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        wnd.set_cursor(dialogmode.DialogCursor(wnd,
                                               [dialogmode.MarkRange('multiline')]))

        wnd.cursor.setpos(self.document.marks['multiline'][0])

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("Canceled")

        if self.callback:
            self.callback(None)

    @command.commandid('multiline.done')
    @command.norec
    @command.norerun
    def multiline_done(self, wnd):
        if self.callback:
            f, t = self.document.marks['multiline']
            s = self.document.gettext(f, t)

        popup = wnd.get_label('popup')
        popup.destroy()

        if self.callback:
            self.callback(s)

    CAPTION = 'Paste text here. Hit alt+Enter when finished:'

    @classmethod
    def build(cls, init_text=''):
        doc = document.Document()
        mode = cls()
        doc.setmode(mode)

        with dialogmode.FormBuilder(doc) as f:
            # caption
            f.append_text('caption', cls.CAPTION)
            f.append_text('default', '\n')
            f.append_text('default', init_text, mark_pair='multiline')

        return doc
