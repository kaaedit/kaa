import curses, os, sys, types, signal
import kaa.tools
import kaa.log
from kaa import options, version, consts, config
from . import app, keydef, frame

from .. import document
from kaa import fileio

CURSES_MOUSEINTERVAL = 200
CURSES_ESCDELAY = '50'

def _init(stdscr):
    if not hasattr(stdscr, 'get_wch'):
        raise RuntimeError(
                'Kaa requires curses library with wide charater support.')
        
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

        mainframe = frame.MainFrame(stdscr)
        kaa.app.init(mainframe)

        if not opt.file:
            # no file args. show new document.
            doc = fileio.newfile(provisional=True)
            kaa.app.show_doc(doc)
        else:
            dirname = None
            for filename in opt.file:
                if os.path.isdir(filename):
                    if not dirname:
                        dirname = filename
                else:
                    doc = kaa.app.storage.openfile(filename)
                    kaa.app.show_doc(doc)
            
            if dirname:
                from kaa.ui.selectfile import selectfile
                def cb(filename, encoding, newline):
                    if filename:
                        doc = kaa.app.storage.openfile(
                                filename, encoding, newline)
                        kaa.app.show_doc(doc)
                    else:
                        if not kaa.app.mainframe.childframes:
                            doc = fileio.newfile(provisional=True)
                            kaa.app.show_doc(doc)
                    
                selectfile.show_fileopen(dirname, cb)
                
        kaa.app.run()
        kaa.app.on_shutdown()

        mainframe.destroy()

    finally:
        _restore()

def handle_term(signum, frame):
    sys.exit(signum+0x80)

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
            term = term+'-256color'
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
