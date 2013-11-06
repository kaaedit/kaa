import difflib
import kaa
from kaa import document
from kaa.filetype.diff import diffmode
from kaa.filetype.default import keybind
from kaa.ui.dialog import dialogmode
from kaa.commands import editorcommand

class ViewDiffMode(dialogmode.DialogMode):
    MODENAME = 'ViewDiff'
    DOCUMENT_MODE = False
    USE_UNDO = False

    def init_commands(self):
        super().init_commands()

        self.cursor_commands = editorcommand.CursorCommands()
        self.register_command(self.cursor_commands)

        self.edit_commands = editorcommand.EditCommands()
        self.register_command(self.edit_commands)

        self.screen_commands = editorcommand.ScreenCommands()
        self.register_command(self.screen_commands)


    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
    ]

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def init_themes(self):
        super().init_themes()
        self.themes.append(diffmode.DiffThemes)

    def init_tokenizers(self):
        self.tokenizers = [diffmode.build_tokenizer()]

    def is_cursor_visible(self):
        return 1   # hide cursor

    def calc_position(self, wnd):
        height = wnd.screen.get_total_height()
        height = min(height, wnd.mainframe.height*3//4)
        top = wnd.mainframe.height - height - wnd.mainframe.MESSAGEBAR_HEIGHT
        return 0, top, wnd.mainframe.width, top+height

    def on_str(self, wnd, s):
        # does nothing
        pass

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        popup.destroy()
        kaa.app.messagebar.set_message("")
        if self.callback:
            self.callback()
        
def view_diff(curdoc, callback=None):
    orig = kaa.app.storage.openfile(
        curdoc.fileinfo.fullpathname, 
        curdoc.fileinfo.encoding, 
        curdoc.fileinfo.newline)
        
    cur_lines = list(curdoc.iterlines(0))
    org_lines = list(orig.iterlines(0))

    diff = ''.join(difflib.unified_diff(org_lines, cur_lines, 
                curdoc.fileinfo.fullpathname, '(buffer)'))
                
    buf = document.Buffer()
    doc = document.Document(buf)
    doc.insert(0, diff)
    
    mode = ViewDiffMode()
    mode.callback = callback
    doc.setmode(mode)

    kaa.app.show_dialog(doc)
    

