import os, unicodedata, sys, locale
import kaa
import kaa.log
from kaa import document, encodingdef
from kaa.filetype.default import defaultmode
from kaa import consts

class FileStorage:
    def get_textio(self, *args, **kwargs):
        try:
            return open(*args, **kwargs)
        except FileNotFoundError:
            return None

    def set_fileinfo(self, fileinfo, filename):
        fullpath = os.path.abspath(filename)
        dirname, filename = os.path.split(filename)

        fileinfo.storage = self
        fileinfo.fullpathname = fullpath
        fileinfo.dirname = dirname
        fileinfo.filename = filename

        try:
            fileinfo.stat = os.stat(filename)
        except FileNotFoundError:
            fileinfo.stat = None
        return fileinfo

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

    def openfile(self, filename, encoding=None, newline=None):
        return openfile(filename, encoding, newline)

    def save_document(self, filename, doc):
        if doc.fileinfo.encoding is None:
            doc.fileinfo.encoding = kaa.app.config.DEFAULT_ENCODING

        if doc.fileinfo.newline is None:
            doc.fileinfo.newline = kaa.app.config.DEFAULT_NEWLINE
        f = open(filename, 'w', encoding=doc.fileinfo.encoding,
                 newline=consts.NEWLINE_CHARS[doc.fileinfo.newline],
                 errors='surrogateescape')
        f.write(doc.gettext(0, doc.endpos()))

        self.set_fileinfo(doc.fileinfo, filename)

        if doc.undo:
            doc.undo.saved()

        mode = select_mode(filename)
        if type(doc.mode) is not mode:
            doc.setmode(mode())

        dir, file = os.path.split(filename)
        if not dir.endswith(os.path.sep):
            dir += os.path.sep

        kaa.app.messagebar.set_message('Written to {}({})'.format(file, dir))


class FileInfo:
    storage = None
    fullpathname = ''
    dirname = ''
    filename = ''
    stat = None
    encoding = None
    newline = None

    def __init__(self):
        self.encoding = kaa.app.config.DEFAULT_ENCODING
        self.newline= kaa.app.config.DEFAULT_NEWLINE

def select_mode(filename):
    ext = os.path.splitext(filename)[1].lower()

    for pkg in kaa.app.config.get_mode_packages():
        if ext in getattr(pkg, 'FILE_EXT', ()):
            return pkg.get_modetype()

    return defaultmode.DefaultMode


def openfile(filename, encoding=None, newline=None):
    # Open file
    if sys.platform == 'darwin':
        filename = unicodedata.normalize('NFC', filename)

    if encoding is None:
        encoding = kaa.app.config.DEFAULT_ENCODING

    if newline is None:
        newline = kaa.app.config.DEFAULT_NEWLINE

    fileinfo = FileInfo()
    kaa.app.storage.set_fileinfo(fileinfo, filename)
    fileinfo.encoding = encoding
    fileinfo.newline = newline
    nlchars = consts.NEWLINE_CHARS[newline]
    # use surrogateescape to preserve file contents intact.
    textio = kaa.app.storage.get_textio(fileinfo.fullpathname, 'r', encoding=encoding,
                                errors='surrogateescape', newline=nlchars)

    buf = document.Buffer()
    if textio:
        src = textio.read()
        if nlchars is not None:
            src = src.replace(nlchars, '\n')
        buf.insert(0, src)

    doc = document.Document(buf)
    doc.fileinfo = fileinfo
    doc.setmode(select_mode(filename)())

    dir, file = os.path.split(fileinfo.fullpathname)
    if not dir.endswith(os.path.sep):
        dir += os.path.sep

    kaa.app.messagebar.set_message('Read from {}({})'.format(file, dir))

    return doc

NUM_NEWFILE = 1
def newfile(mode=None, s=''):
    buf = document.Buffer()
    if s:
        buf.insert(0, s)
    doc = document.Document(buf)

    global NUM_NEWFILE
    doc.title = '<Untitled {}>'.format(NUM_NEWFILE)
    NUM_NEWFILE += 1

    doc.fileinfo = FileInfo()
    if not mode:
        mode = defaultmode.DefaultMode()
    doc.setmode(mode)
    return doc
