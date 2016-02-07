import os
import sys
import subprocess
import shutil
import kaa
import kaa.log


def select_clipboard():
    """Select clipboard class for the platform."""

    if sys.platform == 'darwin':
        return MacClipboard()
    elif X11Clipboard.check():
        return X11Clipboard()
    else:
        return Clipboard()


class Clipboard:

    """Basic clipboard class without platform's native clipboard."""

    # Max history of clipboard entry.
    MAX_CLIPBOARD = 10

    def _get_hist(self):
        return kaa.app.config.hist('clipboard', max_hist=self.MAX_CLIPBOARD)

    def get(self):
        """Get current clipboard entry."""

        all = self.get_all()
        ret = all[0] if all else ''
        if ret:
            self._get_hist().add(ret)
        return ret

    def get_all(self):
        """Get clipboard history."""

        return [s for s, i in self._get_hist().get() if s]

    def _set(self, s):
        self._get_hist().add(s)

    def set(self, s):
        self._set(s)


class NativeClipboard(Clipboard):

    """Base class of platform's native clipboard."""

    def get(self):
        try:
            s = self._get_native_clipboard()
            if s:
                self._set(s)
                return s
            else:
                return super().get()

        except Exception:
            kaa.log.error('Error to copy', exc_info=True)
            return super().get()

    def set(self, s):
        super().set(s)
        try:
            self._set_native_clipboard(s)
        except Exception:
            kaa.log.error('Error to paste', exc_info=True)


class MacClipboard(NativeClipboard):

    """For MAC OS X"""

    COPYCOMMAND = 'pbcopy'
    PASTECOMMAND = 'pbpaste'

    def _get_native_clipboard(self):
        return subprocess.check_output(self.PASTECOMMAND, shell=True,
                                       universal_newlines=True)

    def _set_native_clipboard(self, s):
        p = subprocess.Popen(self.COPYCOMMAND, stdin=subprocess.PIPE,
                             universal_newlines=True, shell=True)
        p.communicate(s)
        p.wait()


class X11Clipboard(NativeClipboard):

    """For UN*X"""

    CLIPCOMMAND = 'xclip'
    COPYCOMMAND = 'xclip -i -selection clipboard'
    PASTECOMMAND = 'xclip  -o -selection clipboard'

    @classmethod
    def check(cls):
        if not shutil.which(X11Clipboard.CLIPCOMMAND):
            return False

        if 'DISPLAY' not in os.environ:
            return False

        return True

    def _get_native_clipboard(self):
        return subprocess.check_output(self.PASTECOMMAND, shell=True,
                                       universal_newlines=True)

    def _set_native_clipboard(self, s):
        p = subprocess.Popen(
            self.COPYCOMMAND,
            stdin=subprocess.PIPE,
            shell=True,
            universal_newlines=True)
        p.stdin.write(s)
        p.stdin.close()
        p.wait()
