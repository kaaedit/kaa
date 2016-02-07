import curses
import curses.panel
import collections

from kaa import log
from kaa.cui import keydef
import kaa.context


class Window(kaa.context.Context):

    """Base class to wrapper of curses.window object

    Class attributes:
        mainframe -- Mainframe of the window
    """

    mainframe = None

    WAITINPUTFOR = 1000  # wait 1000ms for input
    closed = False
    editmode = None
    cursor = None

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

        self.rect = (x, y, x + w, y + h)

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

    def restore_cursor_pos(self):
        if self.cursor:
            x, y = self.cursor.last_screenpos
            if (y, x) != self._cwnd.getyx():
                h, w = self._cwnd.getmaxyx()
                if y < h and x < w and y >= 0 and x >= 0:
                    self._cwnd.move(y, x)

    _keys = []
    _input_lasterror = ''
    _input_skipped = 0

    @classmethod
    def read_console(cls, cwnd, nonblocking):
        if nonblocking:
            cwnd.timeout(0)
        else:
            cwnd.timeout(-1)

        curses.panel.update_panels()
        curses.doupdate()

        last = None
        try:
            while True:
                c = cwnd.get_wch()

                cls._input_lasterror = ''
                cls._input_skipped = 0

                if c == curses.KEY_MOUSE:
                    mouseid, x, y, z, bstate = curses.getmouse()
                    cls._keys.append(keydef.MouseEvent(
                        mouseid, x, y, z, bstate))
                else:
                    cls._keys.extend(keydef.KeyEvent(k, True)
                                     for k in keydef.convert_registered_key(c))
                    last = cls._keys[-1]

                cwnd.timeout(0)

        except curses.error as e:
            if repr(e.args) != cls._input_lasterror:
                if e.args[0] != 'no input':
                    log.debug('Error in get_wch()', exc_info=True)
                cls._input_lasterror = repr(e.args)
            else:
                cls._input_skipped += 1
                if cls._input_skipped % 500 == 0:
                    log.debug(
                        'Too much input-error skips!: {} times'.format(cls._input_skipped))

        # last key event has no trailing character input(i.e. this is not key
        # sequqnce like function keys).
        if last:
            last.has_trailing_char = False

    def do_input(self, nonblocking):
        """Get an input from curses"""

        self._panel.top()

        self.read_console(self._cwnd, nonblocking)

        ret = []
        if self._keys:
            ret.append(self._keys.pop(0))
        return ret

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
            self._cwnd = curses.newwin(b - t, r - l, t, l)
            self.rect = (l, t, r, b)
        except curses.error:
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
        return self.draw_screen()

    def update_status(self):
        return False

    def on_idle(self):
        return

    def on_setrect(self, l, t, r, b):
        """Window resized"""

    def on_focus(self):
        """Got focus"""

    def on_killfocus(self):
        pass
