import os, importlib, unicodedata, sys
import kaa
from kaa import LOG, document
from kaa.filetype.default import defaultmode

class FileStorage:
    def get_textio(self, *args, **kwargs):
        try:
            return open(*args, **kwargs)
        except FileNotFoundError:
            return None

    def get_fileinfo(self, filename):
        fullpath = os.path.abspath(filename)
        dirname, filename = os.path.split(filename)
        ret = FileInfo(self, fullpath, dirname, filename)
        try:
            ret.stat = os.stat(filename)
        except FileNotFoundError:
            ret.stat = None
        return ret

    def listdir(self, dirname):
        dirs = []
        files = []
        for name in os.listdir(dirname):
            if os.path.isdir(os.path.join(dirname, name)):
                dirs.append(name)
            else:
                files.append(name)
        if sys.platform == 'darwin':
            dirs = [unicodedata.normalize('NFC', n) for n in dirs]
            files = [unicodedata.normalize('NFC', n) for n in files]
        return dirs, files

    def openfile(self, filename):
        return openfile(filename)

    def save_document(self, filename, doc):
        open(filename, 'w', encoding='utf-8', errors='surrogateescape').write(doc.gettext(0, doc.endpos()))
        doc.fileinfo = self.get_fileinfo(filename)
        if doc.undo:
            doc.undo.saved()
        mode = select_mode(filename)
        if doc.mode is not mode:
            doc.setmode(mode())
        dir, file = os.path.split(filename)
        if not dir.endswith(os.path.sep):
            dir += os.path.sep

        kaa.app.messagebar.set_message('Written to {}({})'.format(file, dir))

class FileInfo:
    def __init__(self, storage, fullpathname, dirname, filename):
        self.storage = storage
        self.fullpathname = fullpathname
        self.dirname = dirname
        self.filename = filename

class TextInfo:
    def __init__(self, encoding, lf, tabwidth):
        self.encoding = encoding
        self.lf = lf
        self.tabwidth = tabwidth


filetypes = [
    'kaa.filetype.python',
    'kaa.filetype.html',
    'kaa.filetype.javascript',
    'kaa.filetype.css',
]

def select_mode(filename):
    ext = os.path.splitext(filename)[1].lower()
    for pkgname in filetypes:
        try:
            pkg = importlib.import_module(pkgname)
            if ext in getattr(pkg, 'FILE_EXT'):
                return pkg.get_modetype(filename)
        except Exception:
            LOG.exception('Error loading filetype: '+repr(pkgname))

    return defaultmode.DefaultMode


def openfile(filename):
    # Open file
    if sys.platform == 'darwin':
        filename = unicodedata.normalize('NFC', filename)

    fileinfo = kaa.app.storage.get_fileinfo(filename)

    # use surrogateescape to preserve file contents intact.
    textio = kaa.app.storage.get_textio(fileinfo.fullpathname, 'r', encoding=None,
                                errors='surrogateescape', newline=None)

    buf = document.Buffer()
    if textio:
        src = textio.read()
        buf.insert(0, src)

    doc = document.Document(buf)
    doc.setmode(select_mode(filename)())
    doc.fileinfo = fileinfo

    dir, file = os.path.split(fileinfo.fullpathname)
    if not dir.endswith(os.path.sep):
        dir += os.path.sep

    kaa.app.messagebar.set_message('Read from {}({})'.format(file, dir))

    return doc
