import os, importlib, sqlite3, json
import kaa
from kaa import consts, utils

class KaaHistoryStorage:
    def __init__(self, filename):
        self.filename = filename
        self.conn = sqlite3.connect(filename)
        
    def close(self):
        self.conn.close()
        
    def add_history(self, history):
        history.set_storage(self)

    

class History:
    MAX_HISTORY = 999

    def __init__(self, name, storage):
        self.name = name
        self.table_name = 'hist_'+self.name
        self.storage = None

        storage.add_history(self)
        
    @utils.ignore_errors
    def close(self):
        ret = self.storage.conn.execute('''
            SELECT id FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name), (self.MAX_HISTORY, ))
        recs =[value for value in ret]
        if recs:
            last, = recs[-1]
            self.storage.conn.execute('''
                DELETE FROM {} WHERE id < ?
                '''.format(self.table_name), (last,))
            self.storage.conn.commit()
            
    def set_storage(self, storage):
        storage.conn.execute('''
            CREATE TABLE IF NOT EXISTS {}
                (id INTEGER PRIMARY KEY,
                value TEXT,
                info  TEXT)'''.format(self.table_name))
        self.storage = storage

    @utils.ignore_errors
    def add(self, value, info=None):
        if not value:
            return

        ret = self.storage.conn.execute('''
            DELETE FROM {} WHERE value = ?'''.format(self.table_name),
            (value, ))

        self.storage.conn.execute('''
            INSERT INTO {}(value, info) VALUES(?, ?)
            '''.format(self.table_name), (value, json.dumps(info)))

        self.storage.conn.commit()

    def get(self):
        ret = self.storage.conn.execute('''
            SELECT value, info FROM {} ORDER BY id DESC LIMIT ?
            '''.format(self.table_name),
            (self.MAX_HISTORY,))
        return [(value, json.loads(info)) for value,info in ret]

    @utils.ignore_errors
    def find(self, value):
        ret = self.storage.conn.execute('''
            SELECT info FROM {} WHERE value=?
            '''.format(self.table_name),
            (value,))

        for info, in ret:
            return json.loads(info)
        
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
        
    def init_history(self):
        self.hist_storage = KaaHistoryStorage(
            os.path.join(self.HISTDIR, consts.HIST_DBNAME))

        self.hist_files = History('filename', self.hist_storage)
        self.hist_filedisp = History('filedisp', self.hist_storage)
        self.hist_dirs = History('dirname', self.hist_storage)
        self.hist_searchstr = History('search_text', self.hist_storage)
        self.hist_replstr = History('repl_text', self.hist_storage)
        self.hist_grepstr = History('grep_text', self.hist_storage)
        self.hist_grepdir = History('grep_dir', self.hist_storage)
        self.hist_grepfiles = History('grep_filename', self.hist_storage)

    def get_mode_packages(self):
        for pkgname in self.FILETYPES:
            try:
                pkg = importlib.import_module(pkgname)
            except Exception:
                kaa.log.exception('Error loading filetype: '+repr(pkgname))
            else:
                yield pkg
   