import locale
from kaa.ui.multiline import multilinemode
from kaa.keyboard import *


class CommitDialogMode(multilinemode.MultilineMode):

    CAPTION = 'Hit alt+Enter to commit'

    commit_callback = None

    def callback(self, s):
        self.conn.send(b'done')
        self.conn.close()
        self.conn = None
        if s is not None:
            open(self.commitmsg, 'w', encoding=locale.getpreferredencoding()).write(s)

        self.commit_callback()
