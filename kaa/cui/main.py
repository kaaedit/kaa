import curses, os

import kaa
from kaa import options, LOG
from . import app, wnd, keydef, frame

CURSES_MOUSEINTERVAL = 200
CURSES_ESCDELAY = '50'

def _init(stdscr):
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

def main(stdscr):
    _init(stdscr)
    try:
        keydef.init()

        kaa.app = app.CuiApp()
        from kaa import fileio
        kaa.app.storage = fileio.FileStorage()

        mainframe = frame.MainFrame(stdscr)
        kaa.app.init(mainframe)

        from .. import document
        from kaa.filetype.default import defaultmode
        from kaa import fileio

        if not opt.file:
            # no file args. show new document.
            doc = fileio.newfile()
            kaa.app.show_doc(doc)
        else:
            for filename in opt.file:
                doc = kaa.app.storage.openfile(filename)
                kaa.app.show_doc(doc)

        kaa.app.run()

        mainframe.destroy()
    finally:
        _restore()

def run():
    parser = options.build_parser()

    global opt
    opt = parser.parse_args()

    if not os.environ.get('ESCDELAY'):
        os.environ['ESCDELAY'] = CURSES_ESCDELAY
    curses.wrapper(main)


if __name__ == '__main__':
    run()
