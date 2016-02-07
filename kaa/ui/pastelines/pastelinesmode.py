import kaa
from kaa import command
from kaa.ui.multiline import multilinemode
from kaa.keyboard import *


class PasteLinesMode(multilinemode.MultilineMode):

    auto_indent = False

    def close(self):
        super().close()
        self.target = None

    def on_add_window(self, wnd):
        super().on_add_window(wnd)

        kaa.app.messagebar.set_message("Paste text and hit alt+Enter")

    @command.commandid('multiline.done')
    @command.norec
    @command.norerun
    def paste_lines(self, wnd):
        f, t = self.document.marks['multiline']
        s = self.document.gettext(f, t)

        self.target.document.mode.put_string(self.target, s)

        kaa.app.messagebar.set_message("{} letters inserted".format(t - f))

        self.multiline_done(wnd)

    @classmethod
    def build(cls, target):
        doc = super().build()
        doc.mode.target = target

        return doc
