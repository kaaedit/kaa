import curses

class ColorName:
    DEFAULT = -1
    BLACK = curses.COLOR_BLACK
    BLUE = curses.COLOR_BLUE
    CYAN = curses.COLOR_CYAN
    GREEN = curses.COLOR_GREEN
    MAGENTA = curses.COLOR_MAGENTA
    RED = curses.COLOR_RED
    WHITE = curses.COLOR_WHITE
    YELLOW = curses.COLOR_YELLOW

    @classmethod
    def get(cls, name):
        return getattr(cls, name.upper())

class Colors:
    def __init__(self):
        self.pairs = {
            (ColorName.WHITE, ColorName.BLACK):0
        }

    def get_color(self, fg, bg):
        if (fg, bg) not in self.pairs:
            n = len(self.pairs)
            curses.init_pair(n, fg, bg)
            self.pairs[(fg, bg)] = curses.color_pair(n)

        return self.pairs[(fg, bg)]