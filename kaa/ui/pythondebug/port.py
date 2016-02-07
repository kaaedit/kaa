import os
import subprocess
import socket
import json
import kaa
from kaa import document
from kaa.ui.msgbox import msgboxmode
from kaa.ui.inputline import inputlinemode

DEBUGGER = None


class InputReader:

    def get_reader(self):
        if DEBUGGER:
            return DEBUGGER.get_reader()
        else:
            return []

    def read_input(self, f):
        return DEBUGGER.read_input(f)

reader_initialized = False


def init_reader():
    global reader_initialized
    if reader_initialized:
        return
    reader_initialized = True
    # register input_reader
    kaa.app.add_input_reader(InputReader())


def _checkrunning():
    if DEBUGGER:
        if DEBUGGER.session:
            DEBUGGER.show_callstack()
            return True


def init_server():
    global DEBUGGER
    if _checkrunning():
        return

    if isinstance(DEBUGGER, RemoteDebugger):
        DEBUGGER.show_callstack()
        return
    else:
        if DEBUGGER:
            DEBUGGER.close()
            DEBUGGER = None

    def callback(w, s):
        s = s.strip()
        try:
            portno = int(s)
        except ValueError as e:
            kaa.app.messagebar.set_message(str(e))
            return

        global DEBUGGER
        DEBUGGER = RemoteDebugger()
        DEBUGGER.prepare(portno)

        init_reader()

    doc = inputlinemode.InputlineMode.build('Port no:',
                                            callback, value=str(
                                                RemoteDebugger.DEBUGGER_PORT),
                                            filter=inputlinemode.number_filter)

    kaa.app.show_dialog(doc)
    kaa.app.messagebar.set_message(
        'Enter debugger port number (default:28110)')


def run():
    global DEBUGGER
    if _checkrunning():
        return

    if DEBUGGER:
        DEBUGGER.close()
        DEBUGGER = None

    def callback(w, s):
        global DEBUGGER

        s = s.strip()
        if s:
            DEBUGGER = ChildDebugger()
            DEBUGGER.prepare()

            init_reader()

            kaa.app.config.hist('pythondebug_cmdline').add(s)
            DEBUGGER.run(s)

    hist = [s for s, info in kaa.app.config.hist('pythondebug_cmdline').get()]
    if hist:
        value = hist[0]
    else:
        value = 'python3.3 -m kaadbg.run myscript.py arg'

    doc = inputlinemode.InputlineMode.build('Command line:',
                                            callback, value=value, history=hist)
    kaa.app.messagebar.set_message(
        'Enter command line. (e.g python3.3 -m kaadbg.run myscript.py arg)')

    kaa.app.show_dialog(doc)


class BreakPoint:

    def __init__(self, filename, lineno):
        self.filename = filename
        self.lineno = lineno


# todo: Define BreakPoints class
breakpoints = []


def set_breakpoints(filename, bps):
    global breakpoints
    breakpoints = [b for b in breakpoints if b.filename != filename]
    breakpoints.extend(bps)


def get_breakpoints(filename):
    return [b for b in breakpoints if b.filename == filename]


def update_breakpoints():
    for doc in document.Document.all:
        if hasattr(doc.mode, 'update_python_breakpoints'):
            doc.mode.update_python_breakpoints()


class Debugger:
    port = None
    session = None
    current_frames = None
    debugpage = None
    running = False
    kaadbg_ver = None
    kaadbg_pid = None

    def _close_page(self):
        if self.debugpage and not self.debugpage.closed:
            self.debugpage.get_label('popup').destroy()
        self.debugpage = None

    def show_status(self):
        if self.debugpage and not self.debugpage.closed:
            if not self.port and self.is_idle():
                status = '-Closed-'
            elif self.is_idle():
                status = '-Accepting-'
            elif not self.running:
                status = '-BREAK-'
            else:
                status = '-RUNNING-'

            self.debugpage.document.mode.set_status(self.debugpage, status)

    def is_breaking(self):
        return self.session and not self.running

    def set_running(self, running):
        self.running = running

    def is_idle(self):
        return not self.session

    def close(self):
        global DEBUGGER
        DEBUGGER = None

        self.current_frames = None
        self._close_page()

        if self.session:
            self.session.close()
            self.session = None

        if self.port:
            self.port.close()
            self.port = None

    def get_reader(self):
        if not kaa.app.mainframe.is_idle():
            if kaa.app.focus is not self.debugpage:
                # Another form is active.
                return []

        debugger = self.session or self.port
        if debugger:
            return [debugger]
        else:
            return []

    def read_input(self, f):
        if f is self.port:
            self.accept()
        elif f is self.session:
            if not self.read_command():
                self.finished()

    def accept(self):
        if self.session:
            return

        try:
            conn, addr = self.port.accept()
        except BlockingIOError:
            return
        if addr[0] != '127.0.0.1':
            return
        conn.setblocking(True)
        self.session = conn
        self.current_frames = None
        self.breakpoints = []

    def readline(self):
        if not self.session:
            return ''

        L = []
        while True:
            c = self.session.recv(1)
            if not c:
                break
            L.append(c)
            if c == b'\n':
                break

        return b''.join(L)

    def show_callstack(self):
        # update current breakpoints
        update_breakpoints()

        if not self.debugpage or self.debugpage.closed:
            from kaa.ui.pythondebug import pythondebugmode
            wnd = pythondebugmode.show_callstack(self, self.current_frames)
            self.debugpage = wnd

        else:
            self.debugpage.document.mode.update(
                self.debugpage, self.current_frames)

        self.show_status()

    def show_expr_result(self, value):
        def callback(c):
            self.show_callstack()

        self.show_status()
        msgboxmode.MsgBoxMode.show_msgbox(
            'Value: {}'.format(value), ['&Ok'], callback, ['\r', '\n'],
            border=True)

    def read_command(self):
        datalen = self.readline()
        if not datalen:
            return

        datalen = int(datalen)
        if not datalen:
            return

        data = []
        while datalen:
            c = self.session.recv(datalen)
            if not c:
                return

            datalen -= len(c)
            data.append(c)

        self.set_running(False)

        type, value = json.loads(str(b''.join(data), 'utf-8'))
        if type == 'version':
            self.kaadbg_ver = value
        elif type == 'pid':
            self.kaadbg_pid = value
        elif type == 'frame':
            # event = value['event']
            frame = value['frame']
            self.current_frames = frame
            self.show_callstack()
        elif type == 'expr':
            self.show_expr_result(value)
        return True

    def send(self, obj):
        s = (json.dumps(obj) + '\n').encode('utf-8')
        self.session.send(('%d\n' % len(s)).encode('utf-8'))
        self.session.send(s)

    def set_breakpoints(self):
        command = '''
self.clear_all_breaks()
'''
        for bp in breakpoints:
            command += '''
self.set_break({bp.filename!r}, {bp.lineno})
'''.format(bp=bp)
        self.send(('script', command))

    def set_step(self):
        self.set_breakpoints()
        self.show_status()

        command = '''
self.set_step()
ret.append(True)
'''
        self.send(('script', command))

    def set_next(self):
        self.set_breakpoints()
        self.set_running(True)
        self.show_status()

        command = '''
self.set_next(frame)
ret.append(True)
'''
        self.send(('script', command))

    def set_return(self):
        self.set_breakpoints()
        self.set_running(True)
        self.show_status()

        command = '''
self.set_return(frame)
ret.append(True)
'''
        self.send(('script', command))

    def set_continue(self):
        self.set_breakpoints()
        self.set_running(True)
        self.show_status()

        command = '''
self.set_continue()
ret.append(True)
'''
        self.send(('script', command))

    def set_quit(self):
        command = '''
self.set_quit()
ret.append(True)
'''
        self.send(('script', command))

    def get_breakpoints(self):
        return breakpoints

    def del_breakpoint(self, d):
        global breakpoints
        breakpoints = [bp for bp in breakpoints if bp is not d]

    def display_breakpoints(self):
        for doc in document.Document.all:
            if hasattr(doc.mode, 'display_breakpoint'):
                doc.mode.display_breakpoint()

    def show_expr(self, depth, expr):
        command = '''
import io, traceback
try:
    for d in range({depth}):
        frame = frame.f_back
    ret = repr(eval({expr!r}, frame.f_globals, frame.f_locals))
    self.send((u'expr', ret))
except Exception:
    self.send((u'expr', get_tb()))
'''.format(expr=expr, depth=depth)

        self.set_running(True)
        self.show_status()
        self.send(('script', command))


class RemoteDebugger(Debugger):
    DEBUGGER_PORT = 28110

    def prepare(self, portno):

        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        s.bind(('', portno))
        s.listen(5)
        s.setblocking(False)
        self.port = s
        kaa.app.messagebar.set_message(
            'Python debugger server started on port %d.' % portno)

        RemoteDebugger.DEBUGGER_PORT = portno

        self.show_callstack()

    def finished(self):
        if self.session:
            self.session.close()
            self.session = None
            self.current_frames = None
            self._close_page()


class ChildDebugger(Debugger):

    def prepare(self):
        self.session, self.child = socket.socketpair(
            socket.AF_UNIX, socket.SOCK_STREAM)
        kaa.app.messagebar.set_message('Python debugger started.')

    def finished(self):
        self.close()

    def run(self, s):
        env = os.environ.copy()
        env['KAADBG_DOMAINPORT'] = str(self.child.fileno())

        self.set_running(True)
        self.process = subprocess.Popen(s, shell=True,
                                        stdin=subprocess.PIPE,
                                        stdout=subprocess.PIPE, stderr=subprocess.PIPE,
                                        bufsize=1, universal_newlines=True,
                                        pass_fds=(self.child.fileno(),),
                                        env=env)
        self.child.close()

        self.process.stdin.close()
        self.process.stdout.close()
        self.process.stderr.close()

        kaa.app.messagebar.set_message("Process started.")

    def close(self):
        self.set_running(False)
        if self.session:
            try:
                self.set_quit()
            except BrokenPipeError:
                pass
        super().close()
        if self.process:
            self.process.wait()
        kaa.app.mainframe.refresh()
