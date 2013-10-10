import os, importlib, json
import kaa
from kaa import consts

class History(list):
    MAX_HISTORY = 999

    def __init__(self, filename):
        self.filename = filename

    def load(self):
        del self[:]
        if os.path.exists(self.filename):
            try:
                with open(self.filename) as f:
                    items = json.load(f)
                    self.extend(items)

            except Exception as e:
                kaa.log.exception('History file load error:')
                return

    def save(self):
        try:
            with open(self.filename, 'w', encoding='utf-8') as f:
                json.dump(list(self), f)

        except Exception as e:
            kaa.log.exception('History file load error:')
            return

    def add(self, item):
        if not item:
            return
        if item in self:
            self.remove(item)

        self.insert(0, item)
        del self[self.MAX_HISTORY:]


class Config:
    FILETYPES = [
        'kaa.filetype.default',
        'kaa.filetype.python',
        'kaa.filetype.html',
        'kaa.filetype.javascript',
        'kaa.filetype.css',
    ]

    DEFAULT_NEWLINE = 'auto'
    DEFAULT_ENCODING = 'utf-8'

    def __init__(self):
        kaadir = os.path.abspath(
                 os.path.expandvars(
                 os.path.expanduser(consts.KAA_DIR)))

        if not os.path.exists(kaadir):
            os.makedirs(kaadir)

        logdir = os.path.join(kaadir, consts.LOGDIR)
        if not os.path.exists(logdir):
            os.mkdir(logdir)

        histdir = os.path.join(kaadir, consts.HISTDIR)
        if not os.path.exists(histdir):
            os.mkdir(histdir)

        userdir = os.path.join(kaadir, 'kaa')
        if not os.path.exists(userdir):
            os.mkdir(userdir)

        self.KAADIR = kaadir
        self.LOGDIR = logdir
        self.HISTDIR = histdir

        self.hist_files = History(
            os.path.join(self.HISTDIR, consts.HIST_FILENAME))
        self.hist_dirs = History(
            os.path.join(self.HISTDIR, consts.HIST_DIRNAME))
        self.hist_searchstr = History(
            os.path.join(self.HISTDIR, consts.HIST_SEARCH))
        self.hist_replstr = History(
            os.path.join(self.HISTDIR, consts.HIST_REPLACE))

    def get_mode_packages(self):
        for pkgname in self.FILETYPES:
            try:
                pkg = importlib.import_module(pkgname)
            except Exception:
                kaa.log.exception('Error loading filetype: '+repr(pkgname))
            else:
                yield pkg