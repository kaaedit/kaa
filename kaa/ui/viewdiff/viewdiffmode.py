import difflib
import kaa
from kaa import document
from kaa.filetype.diff import diffmode
from kaa.filetype.default import keybind
from kaa.ui.dialog import dialogmode


class ViewDiffMode(dialogmode.DialogMode):
    MODENAME = 'ViewDiff'
    DOCUMENT_MODE = False
    USE_UNDO = False

    KEY_BINDS = [
        keybind.cursor_keys,
        keybind.edit_command_keys,
        keybind.emacs_keys,
        keybind.macro_command_keys,
    ]

    tokenizer = diffmode.make_tokenizer()
    callback = None

    def init_keybind(self):
        super().init_keybind()

        self.register_keys(self.keybind, self.KEY_BINDS)

    def init_themes(self):
        super().init_themes()
        self.themes.append(diffmode.DiffThemes)

    def is_cursor_visible(self):
        return 1   # hide cursor

    def on_str(self, wnd, s, overwrite=False):
        # does nothing
        pass

    def on_esc_pressed(self, wnd, event):
        popup = wnd.get_label('popup')
        if popup:
            popup.destroy()
            kaa.app.messagebar.set_message("")
            if self.callback:
                self.callback()


def view_doc_diff(curdoc, callback=None):
    orig = kaa.app.storage.openfile(
        curdoc.fileinfo.fullpathname,
        curdoc.fileinfo.encoding,
        curdoc.fileinfo.newline,
        nohist=True)

    org_lines = list(orig.iterlines(0))
    orig.close()

    cur_lines = list(curdoc.iterlines(0))
    diff = ''.join(difflib.unified_diff(org_lines, cur_lines,
                                        curdoc.fileinfo.fullpathname, '(buffer)'))

    doc = document.Document()
    doc.insert(0, diff)

    mode = ViewDiffMode()
    mode.callback = callback
    doc.setmode(mode)

    kaa.app.show_dialog(doc)


def show_diff(diff):
    doc = document.Document()
    doc.insert(0, diff)

    mode = ViewDiffMode()
    doc.setmode(mode)

    kaa.app.show_dialog(doc)
