import kaa
from kaa import document, command
from kaa.theme import Theme, Style
from kaa.filetype.default import keybind
from kaa.commands import editorcommand
from kaa.keyboard import *
from kaa.ui.dialog import dialogmode
from kaa.ui.selectlist import filterlist

InputlineThemes = {
    'basic':
        Theme([
        ]),
}

inputline_keys = {
    ('\r'): ('inputline'),
    ('\n'): ('inputline'),
    up: ('inputline.history'),
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

        f, t = self.document.marks['inputtext']
        wnd.cursor.setpos(f)

        if f != t:
            wnd.screen.selection.set_range(f, t)
            
    def on_esc_pressed(self, wnd, event):
        super().on_esc_pressed(wnd, event)
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("Canceled")

    def filter_string(self, wnd, s):
        if self.filter:
            s = self.filter(wnd, s)
        return s

    def get_input_text(self):
        f, t = self.document.marks['inputtext']
        s = self.document.gettext(f, t)
        return s

    def set_input_ext(self, wnd, s):
        cur = self.get_input_text()
        f, t = self.document.marks['inputtext']
        self.document.replace(f, t, s, self.get_styleid('default'))
        f, t = self.document.marks['inputtext']
        wnd.cursor.setpos(f)
        if s:
            wnd.screen.selection.set_range(f, t)

    @command.command('inputline')
    @command.norec
    @command.norerun
    def input_line(self, w):
        s = self.get_input_text()
        self.callback(w, s)
                
        popup = w.get_label('popup')
        popup.destroy()

    @command.command('inputline.history')
    @command.norec
    @command.norerun
    def input_history(self, wnd):
        if not self.history:
            return

        def callback(result):
            if result:
                self.set_input_ext(wnd, result)
            

        filterlist.show_listdlg(self.caption, self.history, callback)

    @classmethod
    def build(cls, caption, callback, filter=None, history=(), value=''):
        buf = document.Buffer()
        doc = document.Document(buf)
        mode = cls()
        doc.setmode(mode)
        mode.caption = caption
        mode.callback = callback
        mode.filter = filter
        mode.history = history
        f = dialogmode.FormBuilder(doc)
    
        # caption
        f.append_text('caption', caption)
        f.append_text('default', ' ')
        f.append_text('default', value, mark_pair='inputtext')

        return doc

