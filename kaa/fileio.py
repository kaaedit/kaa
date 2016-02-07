import os
import unicodedata
import sys
import kaa
import kaa.log
from kaa import document, encodingdef
from kaa.filetype.default import defaultmode
from kaa import consts


class FileStorage:

    def adjust_encoding(self, encoding):
        if encoding.lower() == 'shiftjis':
            return 'cp932'
        encoding = encodingdef.normalize_encname(encoding)
        return encoding

    def guess_japanese_encoding(self, filename):
        import pyjf3
        ret = pyjf3.guess(open(filename, 'rb').read())

        if ret == pyjf3.ASCII:
            return kaa.app.config.DEFAULT_ENCODING
        elif ret == pyjf3.UTF8:
            return 'utf-8'
        elif ret == pyjf3.SJIS:
            return 'cp932'
        elif ret == pyjf3.EUC:
            return 'euc-jp'
        elif ret == pyjf3.JIS:
            return 'iso-2022-jp'
        elif ret == pyjf3.UTF16_LE:
            return 'utf-16le'
        elif ret == pyjf3.UTF16_BE:
            return 'utf-16be'

    def get_textio(self, fileinfo, filemustexists=False):
        try:
            # use surrogateescape to preserve file contents intact.
            textio = open(fileinfo.fullpathname, 'r',
                          encoding=self.adjust_encoding(fileinfo.encoding),
                          errors='surrogateescape',
                          newline=fileinfo.nlchars)

        except FileNotFoundError:
            if filemustexists:
                raise
            return None

        return textio

    def get_fileinfo(self, filename, encoding=None, newline=None):
        if sys.platform == 'darwin':
            filename = unicodedata.normalize('NFC', filename)

        if encoding is None:
            encoding = kaa.app.config.DEFAULT_ENCODING

        if newline is None:
            newline = kaa.app.config.DEFAULT_NEWLINE

        fileinfo = FileInfo()

        fullpath = os.path.abspath(filename)
        dirname, filename = os.path.split(filename)

        fileinfo.storage = self
        fileinfo.fullpathname = fullpath
        fileinfo.dirname = dirname
        fileinfo.filename = filename

        try:
            fileinfo.stat = os.stat(fullpath)
        except FileNotFoundError:
            fileinfo.stat = None

        fileinfo.encoding = encoding
        fileinfo.newline = newline

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

    def _save_hist(self, filename):
        abspath = os.path.abspath(filename)
        dirname = os.path.dirname(abspath)
        if dirname.endswith(os.pathsep):
            dirname = dirname[:-1]

        kaa.app.config.hist('filename').add(abspath)
        kaa.app.config.hist('dirname').add(dirname)
        kaa.app.last_dir = dirname

    def newfile(self, mode=None, s='', temporary=False):
        buf = document.Buffer()
        if s:
            buf.insert(0, s)

        doc = document.Document(buf)
        doc.temporary = temporary

        doc.title = '<Untitled {}>'.format(kaa.app.NUM_NEWFILE)
        kaa.app.NUM_NEWFILE += 1

        doc.fileinfo = FileInfo()
        if not mode:
            mode = defaultmode.DefaultMode()
        doc.setmode(mode)
        return doc

    def openfile(self, filename, encoding=None, newline=None, nohist=False,
                 filemustexists=False, modecls=None):

        fileinfo = self.get_fileinfo(filename, encoding, newline)
        modecls = modecls if modecls else select_mode(fileinfo.fullpathname)
        modecls.update_fileinfo(fileinfo)

        textio = self.get_textio(fileinfo, filemustexists)

        buf = document.Buffer()
        if textio:
            src = textio.read()
            if fileinfo.nlchars is not None:
                src = src.replace(fileinfo.nlchars, '\n')
            buf.insert(0, src)

            if not nohist:
                self._save_hist(filename)

        doc = document.Document(buf)
        doc.fileinfo = fileinfo

        doc.setmode(modecls())

        dir, file = os.path.split(fileinfo.fullpathname)
        if not dir.endswith(os.path.sep):
            dir += os.path.sep

        kaa.app.messagebar.set_message('Read from {}({})'.format(file, dir))

        kaa.app.config.hist_storage.flush()
        return doc

    def save_document(self, doc, filename, encoding=None, newline=None,
                      nohist=False):
        # todo: move most of codes to mode class.
        if not nohist:
            self._save_hist(filename)
        old_fileinfo = doc.fileinfo

        if not doc.fileinfo:
            fileinfo = kaa.app.storage.get_fileinfo(
                filename, encoding, newline)
            doc.fileinfo = fileinfo
        else:
            if encoding is not None:
                doc.fileinfo.encoding = encoding

            if doc.fileinfo.encoding is None:
                doc.fileinfo.encoding = kaa.app.config.DEFAULT_ENCODING

            if newline is not None:
                doc.fileinfo.newline = newline

            if doc.fileinfo.newline is None:
                doc.fileinfo.newline = kaa.app.config.DEFAULT_NEWLINE

        # update mode if file ext was
        old_ext = '' if not old_fileinfo else old_fileinfo.file_ext
        if old_ext.upper() != os.path.splitext(filename)[1].upper():
            modecls = select_mode(filename)
            if type(doc.mode) is not modecls:
                doc.setmode(modecls())

        doc.mode.update_fileinfo(doc.fileinfo, doc)

        with open(filename, 'w',
                  encoding=self.adjust_encoding(doc.fileinfo.encoding),
                  newline=consts.NEWLINE_CHARS[doc.fileinfo.newline],
                  errors='surrogateescape') as f:

            # TODO: save as another file and rename.
            # TODO: fsync
            f.write(doc.gettext(0, doc.endpos()))

        fileinfo = self.get_fileinfo(filename, doc.fileinfo.encoding,
                                     doc.fileinfo.newline)
        doc.mode.on_file_saved(fileinfo)

        doc.fileinfo = fileinfo
        doc.fileinfo.check_update()  # ensure timestamps updated

        doc.set_title(None)
        doc.temporary = False
        if doc.undo:
            doc.undo.saved()

        dir, file = os.path.split(fileinfo.fullpathname)
        if not dir.endswith(os.path.sep):
            dir += os.path.sep

        kaa.app.messagebar.set_message('Written to {}({})'.format(file, dir))

        kaa.app.config.hist_storage.flush()


class FileInfo:
    storage = None
    fullpathname = ''
    dirname = ''
    filename = ''
    stat = None
    encoding = None
    newline = None

    @property
    def nlchars(self):
        return consts.NEWLINE_CHARS[self.newline]

    @property
    def file_ext(self):
        return os.path.splitext(self.fullpathname)[1]

    def __init__(self):
        self.encoding = kaa.app.config.DEFAULT_ENCODING
        self.newline = kaa.app.config.DEFAULT_NEWLINE

    def save_screenloc(self, pos):
        if self.fullpathname:
            info = kaa.app.config.hist('filedisp').find(self.fullpathname)
            if not info:
                info = {}
            info['pos'] = pos
            kaa.app.config.hist('filedisp').add(
                self.fullpathname, info)

    def check_update(self):
        if self.fullpathname:
            try:
                stat = os.stat(self.fullpathname)
            except Exception:
                return

            if stat.st_mtime == self.stat.st_mtime:
                return

            if stat.st_size == self.stat.st_size:
                return

            self.stat = stat
            return True


def select_mode(filename):
    for pkg in kaa.app.config.get_mode_packages():
        if hasattr(pkg, 'FileTypeInfo'):
            ret = pkg.FileTypeInfo.select_mode(filename)
            if ret:
                return ret

    return defaultmode.DefaultMode
