import os
import importlib
import sqlite3
import json
import kaa
from kaa import consts, utils


class KaaHistoryStorage:
    # todo: lock directory for network drives?

    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        self.conn.execute('''
            PRAGMA synchronous = NORMAL
        ''')
        self.hists = {}
        self._updated = False

    BUFFER_DURATION = 10

    def updated(self):
        if not self._updated:
            kaa.app.call_later(self.BUFFER_DURATION, self.flush)
            self._updated = True

    def flush(self):
        try:
            if self._updated:
                for hist in self.hists.values():
                    hist.flush()
                self.conn.commit()
                self._updated = False
        except Exception:
            kaa.log.error('Error saving history', exc_info=True)

    def close(self):
        for hist in self.hists.values():
            hist.flush()

        for hist in self.hists.values():
            hist.close()

        self.conn.commit()
        self.conn.close()
        self.hists = None

    def get_history(self, name, max_hist=None):
        if name not in self.hists:
            hist = History(self, name, max_hist)
            self.hists[name] = hist

        return self.hists[name]


class History:
    MAX_HISTORY = 250

    def __init__(self, storage, name, max_history):
        self.storage = storage
        self.name = name
        self.table_name = 'hist_' + self.name

        self._register()
        self._max_history = max_history
        if not self._max_history:
            self._max_history = self.MAX_HISTORY

        self.buffer = []

    def _register(self):
        self.storage.conn.execute('''
            CREATE TABLE IF NOT EXISTS {}
                (id INTEGER PRIMARY KEY,
                value TEXT,
                info  TEXT)'''.format(self.table_name))

    @utils.ignore_errors
    def close(self):
        ret = self.storage.conn.execute('''
            SELECT id FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name), (self._max_history * 2, ))
        recs = [value for value in ret]
        if recs:
            last, = recs[-1]
            self.storage.conn.execute('''
                DELETE FROM {} WHERE id < ?
                '''.format(self.table_name), (last,))

    @utils.ignore_errors
    def add(self, value, info=None):
        for n, (buf_value, buf_info) in enumerate(self.buffer):
            if value == buf_value:
                del self.buffer[n]
                break
        self.buffer.insert(0, (value, info))
        self.storage.updated()

    def get(self):
        buf_values = set(value for value, info in self.buffer)

        ret = self.storage.conn.execute('''
            SELECT value, info FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name),
            (self._max_history,))

        return self.buffer + [(value, json.loads(info))
                              for value, info in ret if value not in buf_values]

    @utils.ignore_errors
    def find(self, value):
        for buf_value, buf_info in self.buffer:
            if value == buf_value:
                return buf_info

        ret = self.storage.conn.execute('''
            SELECT info FROM {} WHERE value=?
            '''.format(self.table_name),
            (value,))

        for info, in ret:
            return json.loads(info)

    @utils.ignore_errors
    def flush(self):
        # Supress db write if record don't changed.
        if len(self.buffer) == 1:
            ret = self.storage.conn.execute('''
                SELECT value, info FROM {0} as T
                    WHERE T.id = (SELECT max(id) FROM {0})
                '''.format(self.table_name))
            rec = ret.fetchone()
            if rec:
                if self.buffer[0][0] == rec[0]:
                    if self.buffer[0][1] == json.loads(rec[1]):
                        del self.buffer[:]
                        return

        for value, info in self.buffer[::-1]:
            ret = self.storage.conn.execute('''
                DELETE FROM {} WHERE value = ?'''.format(self.table_name),
                                            (value, ))

            self.storage.conn.execute('''
                INSERT INTO {}(value, info) VALUES(?, ?)
                '''.format(self.table_name), (value, json.dumps(info)))
        self.buffer = []


class Config:
    FILETYPES = [
        'kaa.filetype.default',
        'kaa.filetype.python',
        'kaa.filetype.html',
        'kaa.filetype.javascript',
        'kaa.filetype.css',
        'kaa.filetype.diff',
        'kaa.filetype.rst',
        'kaa.filetype.markdown',
        'kaa.filetype.c',
        'kaa.filetype.ini',
        'kaa.filetype.json',
    ]

    DEFAULT_NEWLINE = 'auto'
    DEFAULT_ENCODING = 'utf-8'
    AMBIGUOUS_WIDTH = 1

    def __init__(self, option):
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

        self.KAADIR = kaadir
        self.LOGDIR = logdir
        self.HISTDIR = histdir

        self.palette = option.palette
        self.spellchecker_pwl = os.path.join(kaadir, consts.SPELLCHECKER_PWL)

    def init_history(self):
        self.hist_storage = KaaHistoryStorage(
            os.path.join(self.HISTDIR, consts.HIST_DBNAME))

        self._config = self.hist_storage.get_history('Values')

    def close(self):
        self.hist_storage.close()

    def hist(self, name, max_hist=None):
        return self.hist_storage.get_history(name, max_hist=max_hist)

    def get_mode_packages(self):
        for pkgname in self.FILETYPES:
            try:
                pkg = importlib.import_module(pkgname)
            except Exception:
                kaa.log.exception('Error loading filetype: ' + repr(pkgname))
            else:
                yield pkg

    def save_value(self, name, value):
        self._config.add(name, value)

    def load_value(self, name, default=None):
        values = self._config.get()
        for n, info in values:
            if name == n:
                return info
        return default
