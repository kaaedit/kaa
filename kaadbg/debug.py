import sys
import os
import inspect
import socket
import bdb
import functools
import threading
import json
import locale
import atexit
import time

DEFAULT_PORT_NO = 28110

port = None
lock = threading.RLock()

if sys.version_info[0] >= 3:
    unicode = str


def to_bytes(s):
    if not isinstance(s, bytes):
        s = s.encode('utf-8')
    return s


def dec_filename(fname):
    fname = os.path.abspath(fname)
    if not isinstance(fname, unicode):
        fname = unicode(fname, sys.getfilesystemencoding(),
                        errors='backslashreplace')
    return fname


def dec_locale(l):
    if not isinstance(l, unicode):
        enc = locale.getpreferredencoding()
        l = unicode(l, enc, errors='backslashreplace')
    return l


def from_utf8(s):
    if sys.version_info[0] >= 3:
        return str(s, 'utf-8')
    else:
        return unicode(s, 'utf-8')

import traceback


def _p_exc(info, file):
    if not info:
        info = sys.exc_info()
    try:
        etype, value, tb = info
        traceback.print_exception(etype, value, tb, file=file)
    finally:
        etype = value = tb = None

if sys.version_info[0] >= 3:
    import io

    def get_tb(info=None):
        f = io.StringIO()
        _p_exc(info, f)
        return f.getvalue()
else:
    import cStringIO

    def get_tb(info=None):
        f = cStringIO.StringIO()
        _p_exc(info, f)
        return f.getvalue()


class Kdb(bdb.Bdb):
    closed = False
    _wait_for_mainpyfile = False
    _skip_debug = False
    mainpyfile = None

    def __init__(self):
        bdb.Bdb.__init__(self)

    def exec_file(self, filename):
        import __main__
        __main__.__dict__.clear()
        __main__.__dict__.update({"__name__": "__main__",
                                  "__file__": filename,
                                  "__builtins__": __builtins__,
                                  })

        self._wait_for_mainpyfile = True
        self.mainpyfile = self.canonic(filename)

        with open(filename, "rb") as fp:
            statement = "exec(compile({0!r}, {1!r}, 'exec'))".format(
                fp.read(), self.mainpyfile)
        self.run(statement)

    def connect(self, portno=None):
        if not portno:
            portno = DEFAULT_PORT_NO

        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.connect(('localhost', portno))
        return True

    def run_command(self, frame, obj):
        type, s = obj
        try:
            ret = []
            exec(s, globals(), locals())

            return ret[0] if ret else None
        except Exception:
            self.sock.close()
            raise

    def send(self, obj):
        s = json.dumps(obj) + '\n'
        self.sock.send(to_bytes('%d\n' % len(s)))
        self.sock.send(to_bytes(s))

    def readline(self):
        if not self.sock:
            return b''

        L = []
        while True:
            c = self.sock.recv(1)
            if not c:
                break
            L.append(c)
            if c == b'\n':
                break

        return b''.join(L)

    def recv(self):
        line = self.readline()
        if not line:
            return

        datalen = int(line.strip())
        if not datalen:
            return

        data = []
        while datalen:
            c = self.sock.recv(datalen)
            if not c:
                return

            datalen -= len(c)
            data.append(c)

        type, value = json.loads(from_utf8(b''.join(data)))
        return (type, value)

    def interaction(self, frame):

        frames = []
        for f in inspect.getouterframes(frame):
            _frame, fname, lno, funcname, lines, index = f
            fname = dec_filename(fname)
            if not lines:
                continue
            lines = [dec_locale(l) for l in lines]
            frames.append((fname, lno, funcname, lines))

        self.send((u'frame', frames))

        lines = []
        while True:
            obj = self.recv()
            if not obj:
                self.sock.close()
                break
            if self.run_command(frame, obj):
                break

    def user_line(self, frame):
        if self.in_kdb_code(frame):
            self.set_step()
            return

        if self._wait_for_mainpyfile:
            if (self.mainpyfile != self.canonic(frame.f_code.co_filename)
                    or frame.f_lineno <= 0):
                return
            self._wait_for_mainpyfile = False

        self.interaction(frame)

    def user_exception(self, frame, exc_info):
        exc = get_tb(exc_info)
        self.send((u'expr', exc))
        self.interaction(frame)

    def in_kdb_code(self, frame):
        if not self._skip_debug:
            return

        if os.path.join('kaadbg', 'debug') in frame.f_code.co_filename:
            return True
        else:
            prev_frame = frame.f_back
            if not prev_frame:
                return False

            return self.in_kdb_code(prev_frame)


def set_trace(portno=None):
    with lock:
        global port
        if not port:
            p = Kdb()
            if p.connect(portno):
                port = p

        port.set_trace()
        port._skip_debug = True


@atexit.register
def release():
    global port
    if port:
        port.set_quit()
