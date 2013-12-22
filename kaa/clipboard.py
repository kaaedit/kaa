import sys
import subprocess
import shutil
import kaa


def select_clipboard():
    if sys.platform == 'darwin':
        return MacClipboard()
    elif X11Clipboard.check():
        return X11Clipboard()
    else:
        return Clipboard()


class Clipboard:
    MAX_CLIPBOARD = 10

    def _get_hist(self):
        return kaa.app.config.hist('clipboard', max_hist=self.MAX_CLIPBOARD)

    def get(self):
        all = self.get_all()
        ret = all[0] if all else ''
        if ret:
            self._get_hist().add(ret)
        return ret

    def get_all(self):
        return [s for s, i in self._get_hist().get() if s]

    def _set(self, s):
        self._get_hist().add(s)

    def set(self, s):
        self._set(s)


class NativeClipboard(Clipboard):

    def get(self):
        try:
            s = self._get_native_clipboard()
            if s:
                self._set(s)
            return s
        except Exception:
            kaa.log.error('Error to paste', exc_info=True)
            return super().get()

    def set(self, s):
        super().set(s)
        try:
            self._set_native_clipboard(s)
        except Exception as e:
            pass


class MacClipboard(NativeClipboard):
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
    CLIPCOMMAND = 'xsel'
    COPYCOMMAND = 'xsel -i -b'
    PASTECOMMAND = 'xsel -o -b'

    @classmethod
    def check(cls):
        if not shutil.which(X11Clipboard.CLIPCOMMAND):
            return False

        ret = subprocess.call(cls.CLIPCOMMAND, stdin=subprocess.PIPE,
                              universal_newlines=True, stdout=subprocess.PIPE,
                              stderr=subprocess.PIPE, shell=True)
        if ret:
            return False

        return True

    def _get_native_clipboard(self):
        return subprocess.check_output(self.PASTECOMMAND, shell=True,
                                       universal_newlines=True)

    def _set_native_clipboard(self, s):
        p = subprocess.Popen(self.COPYCOMMAND, stdin=subprocess.PIPE,
                             universal_newlines=True, stdout=subprocess.PIPE,
                             stderr=subprocess.PIPE, shell=True)
        p.communicate(s)
        p.wait()
