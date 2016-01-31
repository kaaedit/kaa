import locale
import kaa
from kaa import document, command
from kaa.ui.multiline import multilinemode
from kaa.theme import Theme, Style
from kaa.filetype.default import keybind
from kaa.commands import editorcommand
from kaa.keyboard import *

class CommitDialogMode(multilinemode.MultilineMode):

    CAPTION = 'Hit alt+Enter to commit'

    @command.commandid('multiline.done')
    @command.norec
    @command.norerun
    def paste_lines(self, wnd):
        f, t = self.document.marks['multiline']
        s = self.document.gettext(f, t)
        open(self.commitmsg, 'w', encoding=locale.getpreferredencoding()).write(s)
        kaa.app.messagebar.set_message("Committed")

        self.multiline_done(wnd)

    def close(self):
        super().close()
        self.conn.send(b'done')
        self.conn.close()
        self.conn = None
        self.wait_for.join()
        self.status_refresh()