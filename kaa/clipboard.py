import sys
import subprocess
import shutil

def select_clipboard():
    if sys.platform == 'darwin':
        return MacClipboard()
    elif shutil.which(X11Clipboard.CLIPCOMMAND):
        return X11Clipboard()
    else:
        return Clipboard()

class Clipboard:
    MAX_CLIPBOARD = 10

    def __init__(self):
        self._clipboard = []

    def get(self):
        self._clipboard[0] if self._clipboard else ''

    def get_all(self):
        return self._clipboard[:]

    def _set(self, s):
        try:
            self._clipboard.remove(s)
        except ValueError:
            pass

        self._clipboard.insert(0, s)
        del self._clipboard[self.MAX_CLIPBOARD:]

    def set(self, s):
        self._set(s)
        
class NativeClipboard(Clipboard):
    def get(self):
        try:
            s = self._get_native_clipboard()
            self._set(s)
            return s
        except Exception:
            return super().get()

    def set(self, s):
        super().set(s)
        try:
            self._set_native_clipboard(s)
        except Exception:
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
    def _get_native_clipboard(self):
        return subprocess.check_output(self.PASTECOMMAND, shell=True, 
                universal_newlines=True)

    def _set_native_clipboard(self, s):
        p = subprocess.Popen(self.COPYCOMMAND, stdin=subprocess.PIPE, 
                universal_newlines=True, stdout=subprocess.PIPE,
                stderr=subprocess.PIPE, shell=True)
        p.communicate(s)
        p.wait()
