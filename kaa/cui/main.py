import threading
import time
import curses
import os
import sys
import types
import signal
import kaa.tools
import kaa.log
from kaa import config
from kaa import options
from kaa import version
from kaa.cui import app, keydef

from kaa import fileio

CURSES_MOUSEINTERVAL = 200
CURSES_ESCDELAY = '50'


def _init(stdscr):
    if not hasattr(stdscr, 'get_wch'):
        raise RuntimeError(
            '''Wide characters are not supported by curses module.
Please install development package for ncursesw library and rebuild Python.

See https://pypi.python.org/pypi/kaaedit/#requirements for detail.
''')

    curses.start_color()
    curses.use_default_colors()

    curses.raw()
    curses.nonl()
    stdscr.leaveok(1)
#    curses.mousemask(curses.ALL_MOUSE_EVENTS)
#    curses.mouseinterval(CURSES_MOUSEINTERVAL)


def _restore():
    curses.noraw()
    curses.nl()


def run_userinit(fname):
    if os.path.isfile(fname):
        with open(fname) as f:
            src = f.read()

        code = compile(src, fname, 'exec')
        module = types.ModuleType('__kaa__')
        exec(code, module.__dict__)

        sys.modules['__kaa__'] = module

URL_CHECKVERSION_HOST = 'http://www.gembook.org'
URL_CHECKVERSION_PATH = '/kaa_checkversion/version_latest'

CHECK_DURARION = 60 * 60 * 24  # check once a day.


def _download_version_no():
    import urllib.request
    import re
    try:
        url = URL_CHECKVERSION_HOST + URL_CHECKVERSION_PATH
        f = urllib.request.urlopen(url, timeout=60)
        s = str(f.read(), 'ascii', errors='replace')
    except Exception:
        return

    m = re.match(r'(\d+)\.(\d+)\.(\d+)', s)
    if m:
        latest = tuple(int(v) for v in m.groups())
        if latest > version.KAA_VERSION:
            kaa.app.messagebar.set_message('')
            kaa.app.call_later(1, kaa.app.messagebar.set_message,
                               'New version of kaa has released.')


def _check_newversion():
    last_checked = kaa.app.config.load_value('time_check_version', 0)
    now = time.time()
    if now - last_checked < CHECK_DURARION:
        return

    kaa.app.config.save_value('time_check_version', now)
    # todo: should not rum in thread
    threading.Thread(target=_download_version_no).start()

opt = None


def main(stdscr):
    conf = config.Config(opt)
    sys.path.insert(0, conf.KAADIR)

    kaa.log.init(conf.LOGDIR)

    _init(stdscr)
    try:
        keydef.init(conf)

        kaa.app = app.CuiApp(conf)
        kaa.app.storage = fileio.FileStorage()

        if not opt.no_init:
            fname = opt.init_script
            if not fname:
                fname = os.path.join(kaa.app.config.KAADIR, '__kaa__.py')
            run_userinit(fname)

        from kaa.cui import frame
        mainframe = frame.MainFrame(stdscr)
        kaa.app.init(mainframe)

        if not opt.file:
            # no file args. show new document.
            doc = kaa.app.storage.newfile(temporary=True)
            kaa.app.show_doc(doc)
        else:
            dirname = None
            for filename in opt.file:
                if os.path.isdir(filename):
                    if not dirname:
                        dirname = filename
                else:
                    doc = kaa.app.storage.openfile(filename)
                    editor = kaa.app.show_doc(doc)
                    kaa.app.file_commands.restore_file_loc(editor)

            if dirname:
                from kaa.ui.selectfile import selectfile

                def cb(filename, encoding, newline):
                    if filename:
                        doc = kaa.app.storage.openfile(
                            filename, encoding, newline)
                        kaa.app.show_doc(doc)
                    else:
                        if not kaa.app.mainframe.childframes:
                            doc = kaa.app.storage.newfile(temporary=True)
                            kaa.app.show_doc(doc)

                selectfile.show_fileopen(dirname, cb)

        if opt.command:
            cmd = kaa.app.focus.document.mode.get_command(
                opt.command)
            is_available, command = cmd
            if command:
                command(kaa.app.focus)
            else:
                sys.exit('Unknown command: {}'.format(opt.command))

#        kaa.app.call_later(10, _check_newversion)
        kaa.app.run()
        mainframe.destroy()
        kaa.app.on_shutdown()

    finally:
        _restore()


def handle_term(signum, frame):
    sys.exit(signum + 0x80)

COLOR_ENVS = ('COLORTERM', 'XTERM_VERSION', 'ROXTERM_ID',
              'KONSOLE_DBUS_SESSION')


def _init_term():
    if opt.term:
        os.environ['TERM'] = opt.term

    # http://fedoraproject.org/wiki/Features/256_Color_Terminals
    for env in COLOR_ENVS:
        if os.environ.get(env):
            has_color = True
            break
    else:
        has_color = False

    if has_color:
        term = os.environ.get('TERM')

        if term in ('xterm', 'screen', 'Eterm'):
            term = term + '-256color'
            os.environ['TERM'] = term

        if os.environ.get('TERM', '') == 'screen-256color':
            termcap = os.environ.get('TERMCAP')
            if termcap:
                os.environ['TERMCAP'] = termcap.replace('Co#8', 'Co#256')


def run():
    if sys.version_info[:2] < (3, 3):
        raise RuntimeError('kaa requires Python 3.3 or later')

    if not getattr(__builtins__, 'kaa_freeze', False):
        try:
            setproctitle = __import__('setproctitle')
            setproctitle.setproctitle('kaa')
        except:
            pass

    signal.signal(signal.SIGTERM, handle_term)

    parser = options.build_parser()

    global opt
    opt = parser.parse_args()

    if opt.show_version:
        print(version.version_info())
        return

    if not os.environ.get('ESCDELAY'):
        os.environ['ESCDELAY'] = CURSES_ESCDELAY

    _init_term()
    curses.wrapper(main)


if __name__ == '__main__':
    run()
