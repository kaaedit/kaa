import curses, curses.panel
import collections

from kaa import log
from kaa.cui import keydef
import kaa.context
from kaa import editmode

class Window(kaa.context.Context):
    """Base class to wrapper of curses.window object

    Class attributes:
        mainframe -- Mainframe of the window
    """

    mainframe = None

    WAITINPUTFOR = 1000 # wait 1000ms for input
    closed = False
    editmode = None
    def __init__(self, parent, wnd=None, pos=None):
        """Wrap window object wnd. Create new window if wnd was omitted."""

        super().__init__()

        w, h = 1, 1
        x = y = 0
        if parent:
            w, h = parent.getsize()

        if wnd:
            self._cwnd = wnd
        else:
            if pos:
                x, y = pos
            else:
                x = y = 0

            w = max(1, w)
            h = max(1, h)
            self._cwnd = curses.newwin(h, w, y, x)

        self._panel = curses.panel.new_panel(self._cwnd)
        self._cwnd.keypad(1)
        self.parent = parent
        self.children = []
        if self.parent:
            self.parent.children.append(self)

        self.rect = (x, y, x+w, y+h)

        self._oninit()

    def _oninit(self):
        pass

    def walk_children(self):
        # breadth first
        stack = collections.deque([self])
        while stack:
            v = stack.pop()
            if v is not self:
                yield v
            stack.extendleft(v.children)

    def destroy(self):
        """Destroy window"""
        if self.closed:
            return
        self.closed = True
        while self.children:
            self.children[0].destroy()

        if self.parent:
            self.parent.children.remove(self)
        self.parent = None
        self._cwnd = self._panel = None

        if kaa.app.focus is self:
            kaa.app.focus = None

    def get_context_parent(self):
        return self.parent

    _lasterror = ''
    _skipped = 0
    def do_input(self, nonblocking):
        """Get an input from curses"""
        self.bring_top()
        if nonblocking:
            self._cwnd.timeout(0)
        else:
            self._cwnd.timeout(-1)
#            self._cwnd.timeout(self.WAITINPUTFOR)

        no_trailing_char = False  # true if esc key pressed
        try:
            curses.panel.update_panels()
            curses.doupdate()

            c = self._cwnd.get_wch()
            if c == '\x1b':
                self._cwnd.timeout(0)
                try:
                    c2 = self._cwnd.get_wch()
                    # has trailing character.
                    curses.unget_wch(c2)
                except curses.error:
                    # no trailing character.
                    no_trailing_char = True

        except curses.error as e:
            if repr(e.args) != self._lasterror:
                if e.args[0] != 'no input':
                    log.debug('Error in get_wch()', exc_info=True)
                self._lasterror = repr(e.args)
            else:
                self._skipped += 1
                if self._skipped % 500 == 0:
                    log.debug('Too much input-error skips!: {} times'.format(self._skipped))
            return []

        self._lasterror = ''
        self._skipped = 0

        if c == curses.KEY_MOUSE:
            mouseid, x, y, z, bstate = curses.getmouse()
            keys = [keydef.MouseEvent(self, mouseid, x, y, z, bstate)]
        else:
            keys = [keydef.KeyEvent(self, k, no_trailing_char)
                    for k in keydef.convert_registered_key(c)]

#        for k in keys:
#            _trace('{!r}'.format(k))

        return keys

    def add_str(self, letters, attr):
        try:
            self._cwnd.addstr(letters, attr)
        except curses.error:
            # exception is raised if a characters are written
            # over right border.
#            logstr = letters if (len(letters) < 10) else (letters[:10]+'...')
#            log.debug('Error to write str:{!r}'.format(logstr), exc_info=True)
            pass

    def bring_top(self):
        self._panel.top()

    def activate(self):
        """Activate wnd"""
        self.bring_top()
        kaa.app.set_focus(self)
        
    def set_rect(self, l, t, r, b):
        """Set window coordinate"""

        if hasattr(self, 'splitter') and self.splitter:
            assert t <= self.splitter.rect[1]

        try:
            self._cwnd = curses.newwin(b-t, r-l, t, l)
            self.rect = (l, t, r, b)
        except curses.error as e:
            log.debug('error on resizing window: {} {}'.format(self,
                                       (l, t, r, b), exc_info=True))
            # shrink window to avoid segfault in curses
            self._cwnd = curses.newwin(1, 1, 0, 0)
            self.rect = (0, 0, 1, 1)

         # surprisingly enough, the following assert fails sometime.
#        t, l = self._cwnd.getbegyx()
#        h, w = self._cwnd.getmaxyx()
#        assert (l, t, l+w, t+h) == self.rect

        self._cwnd.keypad(1)

        self._panel = curses.panel.new_panel(self._cwnd)
        self.on_setrect(*self.rect)


    def draw_screen(self, force=False):
        pass

    def getsize(self):
        h, w = self._cwnd.getmaxyx()
        return w, h

    def refresh(self):
        self.mainframe.request_refresh()

    def update_window(self):
        self.draw_screen()

    def update_status(self):
        return False

    def on_idle(self):
        return

    def on_setrect(self, l, t, r, b):
        """Window resized"""
        pass

    def on_focus(self):
        """Got focus"""
        pass

    def on_killfocus(self):
        pass

