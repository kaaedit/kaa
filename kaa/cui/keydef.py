import curses
import curses_ex
import io
import os
from kaa.keyboard import *

KAA_KEYCODE_FROM = 1000

BUTTONNAMES = {
    curses.BUTTON1_CLICKED: "BUTTON1_CLICKED",
    curses.BUTTON1_DOUBLE_CLICKED: "BUTTON1_DOUBLE_CLICKED",
    curses.BUTTON1_PRESSED: "BUTTON1_PRESSED",
    curses.BUTTON1_RELEASED: "BUTTON1_RELEASED",
    curses.BUTTON1_TRIPLE_CLICKED: "BUTTON1_TRIPLE_CLICKED",
    curses.BUTTON2_CLICKED: "BUTTON2_CLICKED",
    curses.BUTTON2_DOUBLE_CLICKED: "BUTTON2_DOUBLE_CLICKED",
    curses.BUTTON2_PRESSED: "BUTTON2_PRESSED",
    curses.BUTTON2_RELEASED: "BUTTON2_RELEASED",
    curses.BUTTON2_TRIPLE_CLICKED: "BUTTON2_TRIPLE_CLICKED",
    curses.BUTTON3_CLICKED: "BUTTON3_CLICKED",
    curses.BUTTON3_DOUBLE_CLICKED: "BUTTON3_DOUBLE_CLICKED",
    curses.BUTTON3_PRESSED: "BUTTON3_PRESSED",
    curses.BUTTON3_RELEASED: "BUTTON3_RELEASED",
    curses.BUTTON3_TRIPLE_CLICKED: "BUTTON3_TRIPLE_CLICKED",
    curses.BUTTON4_CLICKED: "BUTTON4_CLICKED",
    curses.BUTTON4_DOUBLE_CLICKED: "BUTTON4_DOUBLE_CLICKED",
    curses.BUTTON4_PRESSED: "BUTTON4_PRESSED",
    curses.BUTTON4_RELEASED: "BUTTON4_RELEASED",
    curses.BUTTON4_TRIPLE_CLICKED: "BUTTON4_TRIPLE_CLICKED",
    curses.BUTTON_ALT: "BUTTON_ALT",
    curses.BUTTON_CTRL: "BUTTON_CTRL",
    curses.BUTTON_SHIFT: "BUTTON_SHIFT",
}


class KeyEvent:

    """ Stores information of keyboard input event.

    Attributes:
        key -- key code returned by curses.
    """
    KEY_TRANSLATE = {
        curses.KEY_BACKSPACE: '\x7f'
    }

    def __init__(self, key, has_trailing_char):
        """

        Auguments:
            key -- key code returned by curses.

        """

        self.key = self.KEY_TRANSLATE.get(key, key)
        self.has_trailing_char = has_trailing_char

    def __repr__(self):
        c = self.key if isinstance(self.key, int) else ord(self.key)
        name = str(curses.keyname(c), 'ascii', 'replace')
        return '<key: {!r} {}'.format(name, super().__repr__())

    def unget(self):
        curses.unget_wch(self.key)


class MouseEvent:

    """ Stores information of mouse input event.

    Attributes:
        x, y -- Event coordinates
        code -- Type of event
        shift -- True if shift key was pressed
        ctrl -- True if control key was pressed
        alt -- True if alt key was pressed
    """

    def __init__(self, mouseid, x, y, z, bstate):
        self.mouseid = mouseid
        self.x = x
        self.y = y
        self.z = z
        self.bstate = bstate

        self.code = bstate & ~(curses.BUTTON_SHIFT | curses.BUTTON_CTRL |
                               curses.BUTTON_ALT)

        self.shift = bstate & curses.BUTTON_SHIFT
        self.ctrl = bstate & curses.BUTTON_CTRL
        self.alt = bstate & curses.BUTTON_ALT

    @property
    def button1clicked(self):
        """True if code is BUTTON1_CLICKED"""

        return self.code == curses.BUTTON1_CLICKED

    @property
    def button2clicked(self):
        """True if code is BUTTONR2_CLICKED"""

        return self.code == curses.BUTTON2_CLICKED

    @property
    def button3clicked(self):
        """True if code is BUTTON3_CLICKED"""

        return self.code == curses.BUTTON3_CLICKED

    def __repr__(self):
        name = BUTTONNAMES.get(self.code, self.code)
        name = hex(name) if isinstance(name, int) else name

        mods = "".join((('M-' if self.alt else ''),
                        ('^' if self.ctrl else ''),
                        ('SHIFT+' if self.shift else '')))

        return '<mouse: ({},{}) - {}{} {}>'.format(
            self.x, self.y, mods, name, super().__repr__())

    def unget(self):
        curses.ungetmouse(self.mouseid, self.x, self.y, self.z, self.bstate)


KEYNAME_CURSES = {
    backspace: '\x7f',
    delete: curses.KEY_DC,
    pageup: curses.KEY_PPAGE,
    pagedown: curses.KEY_NPAGE,
    left: curses.KEY_LEFT,
    right: curses.KEY_RIGHT,
    up: curses.KEY_UP,
    down: curses.KEY_DOWN,
    home: curses.KEY_HOME,
    end: curses.KEY_END,
    tab: '\t',
    esc: '\x1b',
    f1: curses.KEY_F1,
    f2: curses.KEY_F2,
    f3: curses.KEY_F3,
    f4: curses.KEY_F4,
    f5: curses.KEY_F5,
    f6: curses.KEY_F6,
    f7: curses.KEY_F7,
    f8: curses.KEY_F8,
    f9: curses.KEY_F9,
    f10: curses.KEY_F10,
    f11: curses.KEY_F11,
    f12: curses.KEY_F12,
    f13: curses.KEY_F13,
    f14: curses.KEY_F14,
    f15: curses.KEY_F15,
    f16: curses.KEY_F16,
    f17: curses.KEY_F17,
    f18: curses.KEY_F18,
    f19: curses.KEY_F19,
    f20: curses.KEY_F20,
    f21: curses.KEY_F21,
    f22: curses.KEY_F22,
    f23: curses.KEY_F23,
    f24: curses.KEY_F24,
}


KEYNAME_CURSES_SHIFT = {
    tab: curses.KEY_BTAB,
    delete: curses.KEY_SDC,
    home: curses.KEY_SHOME,
    end: curses.KEY_SEND,
    left: curses.KEY_SLEFT,
    right: curses.KEY_SRIGHT,
    up: curses.KEY_SR,
    down: curses.KEY_SF
}

KEYNAME_TO_CODE = {
    # (ctrl, shift, key) : keycode
    (0, 0, backspace): '\x7f',
    (0, 0, delete): curses.KEY_DC,
    (0, 0, pageup): curses.KEY_PPAGE,
    (0, 0, pagedown): curses.KEY_NPAGE,
    (0, 0, left): curses.KEY_LEFT,
    (0, 0, right): curses.KEY_RIGHT,
    (0, 0, up): curses.KEY_UP,
    (0, 0, down): curses.KEY_DOWN,
    (0, 0, home): curses.KEY_HOME,
    (0, 0, end): curses.KEY_END,
    (0, 0, tab): '\t',
    (0, 0, esc): '\x1b',
    (0, 0, f1): curses.KEY_F1,
    (0, 0, f2): curses.KEY_F2,
    (0, 0, f3): curses.KEY_F3,
    (0, 0, f4): curses.KEY_F4,
    (0, 0, f5): curses.KEY_F5,
    (0, 0, f6): curses.KEY_F6,
    (0, 0, f7): curses.KEY_F7,
    (0, 0, f8): curses.KEY_F8,
    (0, 0, f9): curses.KEY_F9,
    (0, 0, f10): curses.KEY_F10,
    (0, 0, f11): curses.KEY_F11,
    (0, 0, f12): curses.KEY_F12,
    (0, 0, f13): curses.KEY_F13,
    (0, 0, f14): curses.KEY_F14,
    (0, 0, f15): curses.KEY_F15,
    (0, 0, f16): curses.KEY_F16,
    (0, 0, f17): curses.KEY_F17,
    (0, 0, f18): curses.KEY_F18,
    (0, 0, f19): curses.KEY_F19,
    (0, 0, f20): curses.KEY_F20,
    (0, 0, f21): curses.KEY_F21,
    (0, 0, f22): curses.KEY_F22,
    (0, 0, f23): curses.KEY_F23,
    (0, 0, f24): curses.KEY_F24,

    (0, 1, tab): curses.KEY_BTAB,
    (0, 1, delete): curses.KEY_SDC,
    (0, 1, home): curses.KEY_SHOME,
    (0, 1, end): curses.KEY_SEND,
    (0, 1, left): curses.KEY_SLEFT,
    (0, 1, right): curses.KEY_SRIGHT,
    (0, 1, up): curses.KEY_SR,
    (0, 1, down): curses.KEY_SF,
    (0, 1, pagedown): curses.KEY_SNEXT,
    (0, 1, pageup): curses.KEY_SPREVIOUS,
}


def keyfromname(key, ctrl, shift):
    return KEYNAME_TO_CODE.get((ctrl, shift, key))


def convert_registered_key(key):
    if key in REGISTERD_SEQUENCE:
        return REGISTERD_SEQUENCE[key]
    else:
        return [key]

# works for xterm?
CAPNAME_TO_KEY = {
    # capname: (ctrl, shift, key),
    'kHOM5': (1, 0, home),
    'kHOM6': (1, 1, home),
    'kEND5': (1, 0, end),
    'kEND6': (1, 1, end),
    'kLFT5': (1, 0, left),
    'kLFT6': (1, 1, left),
    'kRIT5': (1, 0, right),
    'kRIT6': (1, 1, right),
    'kUP5': (1, 0, up),
    'kUP6': (1, 1, up),
    'kDN5': (1, 0, down),
    'kDN6': (1, 1, down),
    'kPRV5': (1, 0, pageup),
    'kPRV6': (1, 1, pageup),
    'kNXT5': (1, 0, pagedown),
    'kNXT6': (1, 1, pagedown),
    'kDC5': (1, 0, delete),
    'kDC6': (1, 1, delete),
}

# http://pubs.opengroup.org/onlinepubs/7908799/xcurses/terminfo.html
CAPNAME_TO_CODE = {
    'cuf1': curses.KEY_RIGHT,
    'kcuf1': curses.KEY_RIGHT,
    'kRIT': curses.KEY_SRIGHT,
    'kcub1': curses.KEY_LEFT,
    'kcuu1': curses.KEY_UP,
    'kri': curses.KEY_SR,
    'kcud1': curses.KEY_DOWN,
    'kind': curses.KEY_SF,
    'kDN': curses.KEY_SF,
    'khome': curses.KEY_HOME,
    'kHOM': curses.KEY_SHOME,
    'kend': curses.KEY_END,
    'kEND': curses.KEY_SEND,
    'kpp': curses.KEY_PPAGE,
    'knp': curses.KEY_NPAGE,
}

# Terminals like iTerm2 sends following codes for alt+cursor keys
KNOWN_KEY_SEQUENCE = {
    b'\x1b\x1b[A': ['\x1b', curses.KEY_UP],
    b'\x1b\x1b[B': ['\x1b', curses.KEY_DOWN],
    b'\x1b\x1b[C': ['\x1b', curses.KEY_RIGHT],
    b'\x1b\x1b[D': ['\x1b', curses.KEY_LEFT],
}

REGISTERD_SEQUENCE = {}


def init(conf):
    # Experimental code to get keycode from cap name
    for i in range(512, 1024):
        name = str(curses.keyname(i), 'utf-8', 'replace')
        if name in CAPNAME_TO_KEY:
            KEYNAME_TO_CODE[CAPNAME_TO_KEY[name]] = i
            CAPNAME_TO_CODE[name] = i

    result = io.StringIO()
    err = False

    reg_code = KAA_KEYCODE_FROM
    # register ESC + seq
    registered_seqs = set()
    for name, keycode in CAPNAME_TO_CODE.items():
        seq = curses.tigetstr(name)
        if seq:
            seq = b'\x1b' + seq
            try:
                curses_ex.define_key(seq, reg_code)
                print('OK: ', name, keycode, reg_code, seq, file=result)
            except Exception:
                print('NG: ', name, keycode, reg_code, seq, file=result)
                continue

            REGISTERD_SEQUENCE[reg_code] = ['\x1b', keycode]
            reg_code += 1
            registered_seqs.add(seq)

    for seq, keycode in KNOWN_KEY_SEQUENCE.items():
        if seq not in registered_seqs:
            try:
                curses_ex.define_key(seq, reg_code)
                print('OK: ', keycode, reg_code, seq, file=result)
            except Exception:
                print('NG: ', keycode, reg_code, seq, file=result)
                continue

            REGISTERD_SEQUENCE[reg_code] = keycode
            reg_code += 1

    logname = os.path.join(conf.LOGDIR, 'DEFINE_KEY.LOG')
    with open(logname, 'w') as f:
        f.write(result.getvalue())
