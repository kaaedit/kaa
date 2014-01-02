import itertools
import re
import unicodedata
import kaa
from kaa.command import Commands, commandid, is_enable, norec, norerun
from kaa import document
from kaa.filetype.default import modebase
from kaa import doc_re


class ViCommands(Commands):

    @commandid('edit.replace-char')
    @norec
    @norerun
    def replace_char(self, wnd):
        wnd.editmode.install_keyhook(self.hook_replacechar)

    def hook_replacechar(self, wnd, keyevent):
        s = keyevent.key[0]
        if s >= ' ':
            wnd.document.mode.put_string(wnd, s, overwrite=True)
            return None
        return keyevent
