import kaa
from kaa.commands import appcommand, filecommand, editorcommand, modecommand
from . import keybind, theme, modebase

from kaa import highlight

class DefaultMode(modebase.ModeBase):
    def init_keybind(self):
        super().init_keybind()

        self.keybind.add_keybind(keybind.app_keys)
        self.keybind.add_keybind(keybind.cursor_keys)
        self.keybind.add_keybind(keybind.edit_command_keys)
        self.keybind.add_keybind(keybind.emacs_keys)
        self.keybind.add_keybind(keybind.search_command_keys)
        self.keybind.add_keybind(keybind.macro_command_keys)

    def init_vikeybind(self):
        super().init_vikeybind()

        self.keybind_vi_normalmode.add_keybind(keybind.normal_mode_keys)
        self.keybind_vi_visualmode.add_keybind(keybind.visual_mode_keys)
        self.keybind_vi_visuallinewisemode.add_keybind(
            keybind.visual_linewise_mode_keys)

    def init_commands(self):
        super().init_commands()

        self.app_commands = appcommand.ApplicationCommands()
        self.register_command(self.app_commands)

        self.file_commands = filecommand.FileCommands()
        self.register_command(self.file_commands)

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands)

        self.edit_commands = editorcommand.EditCommands()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)

        self.macro_commands = editorcommand.MacroCommands()
        self.register_command(self.macro_commands)

        self.search_commands = editorcommand.SearchCommands()
        self.register_command(self.search_commands)

        self.mode_commands = modecommand.ModeCommands()
        self.register_command(self.mode_commands)

    def init_theme(self):
        self.theme = theme.DefaultTheme

    def init_tokenizers(self):
        self.tokenizers = [highlight.Tokenizer([])]

    def close(self):
        super().close()
        self.keybind_vi_normalmode.clear()
        self.keybind_vi_visualmode.clear()
        self.keybind_vi_visuallinewisemode.clear()


    HIGHLIGHTBATCH = 300
    def run_highlight(self):
        return self.highlight.update_style(self.document, batch=self.HIGHLIGHTBATCH)

    def on_esc_pressed(self, wnd, event):
        is_available, command = self.get_command('mode.normal')
        if command:
            command(wnd)
            if kaa.app.macro.is_recording():
                kaa.app.macro.record(command)





