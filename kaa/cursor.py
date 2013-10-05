class Cursor:
    def __init__(self, wnd):
        self.wnd = wnd
        self.pos = 0
        self.preferred_col = 0

    def refresh(self, top=None, middle=None, bottom=None):
        self.pos, y, x = self.wnd.locate_cursor(self.pos, top=top, middle=middle, bottom=bottom)
        assert self.pos is not None

    def setpos(self, pos, top=None, middle=None, bottom=None):
        assert pos is not None

        self.pos = pos
        self.refresh(top=top, middle=middle, bottom=bottom)

    def savecol(self):
        """Update current preferred column"""

        y, x = self.wnd.screen.getrowcol(self.pos)
        self.preferred_col = x

    def up(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)
        idx, row = self.wnd.screen.getrow(self.pos)
        if row.posfrom == 0:
            return

        if idx == self.wnd.screen.portfrom:
            # Scroll up a line
            if not self.wnd.lineup():
                # First line of text file
                return False
            idx, prevrow = self.wnd.screen.getrow(row.posfrom-1)
        else:
            idx -= 1
        pos = self.wnd.screen.get_pos_above(idx, self.preferred_col)
        self.setpos(pos)
        return True

    def down(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)
        idx, row = self.wnd.screen.getrow(self.pos)

        if self.wnd.screen.is_lastrow(row):
            return False

        if idx+1 >= self.wnd.screen.portto:
            # Scroll down a line
            if not self.wnd.linedown():
                # last line of text file
                return False
            idx, nextrow = self.wnd.screen.getrow(row.posto)
        else:
            idx += 1

        pos = self.wnd.screen.get_pos_under(idx, self.preferred_col)
        self.setpos(pos)

        return True

    def adjust_nextpos(self, curpos, nextpos):
        return nextpos

    def right(self, word=False):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        if self.pos == self.wnd.document.endpos():
            return

        if not word:
            # Get right of current position
            nextpos = self.wnd.document.get_nextpos(self.pos)
        else:
            # Get next word break
            nextpos = self.wnd.document.endpos()
            for word in self.wnd.document.mode.split_word(self.pos):
                f, t, chars = word
                nextpos = t
                if f == self.pos: # first word
                    # get next word
                    continue
                nextpos = f
                break

        nextpos = self.adjust_nextpos(self.pos, nextpos)
        if nextpos != self.pos:
            # Scroll down if next position is not visible
            while not self.wnd.screen.is_visible(nextpos):
                # scroll down
                if not self.wnd.linedown():
                    break

            self.setpos(nextpos)
            self.savecol()

    def left(self, word=False):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        if self.pos == 0:
            return

        if not word:
            # Get left of current position
            prevpos = self.wnd.document.get_prevpos(self.pos)
        else:
            # Get previous word break
            prevpos = tol = self.wnd.document.gettol(self.pos)
            if self.pos == prevpos:
                prevpos -= 1
            else:
                for f, t, chars in self.wnd.document.mode.split_word(tol):
                    #  This word is at after cursor pos
                    if self.pos <= f:
                        break

                    prevpos = f

        prevpos = self.adjust_nextpos(self.pos, prevpos)
        if prevpos != self.pos:
            # Scroll up if next position is not visible
            while not self.wnd.screen.is_visible(prevpos):
                # scroll up
                if not self.wnd.lineup():
                    break

            self.setpos(prevpos)
            self.savecol()

    def pagedown(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        idx, row = self.wnd.screen.getrow(self.pos)
        y = idx - self.wnd.screen.portfrom

        if self.wnd.pagedown():
            idx = max(0, min(self.wnd.screen.portto-1,
                             self.wnd.screen.portfrom+y))
            pos = self.wnd.screen.get_pos_under(idx, self.preferred_col)

            nextpos = self.adjust_nextpos(self.pos, pos)
            self.setpos(nextpos)

            return True

    def pageup(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        idx, row = self.wnd.screen.getrow(self.pos)
        y = idx - self.wnd.screen.portfrom

        if self.wnd.pageup():
            idx = max(0, min(self.wnd.screen.portto-1,
                             self.wnd.screen.portfrom+y))
            pos = self.wnd.screen.get_pos_above(idx, self.preferred_col)
            nextpos = self.adjust_nextpos(self.pos, pos)
            self.setpos(nextpos)

            return True

    def home(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        idx, row = self.wnd.screen.getrow(self.pos)
        nextpos = self.adjust_nextpos(self.pos, row.posfrom)
        self.setpos(nextpos)
        self.savecol()

    def end(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        idx, row = self.wnd.screen.getrow(self.pos)
        if self.wnd.screen.is_lastrow(row):
            pos = self.wnd.document.endpos()
        else:
            pos = row.posto-1

        nextpos = self.adjust_nextpos(self.pos, pos)
        self.setpos(nextpos)
        self.savecol()

    def tof(self):
        self.wnd.screen.locate(0, top=True)
        nextpos = self.adjust_nextpos(self.pos, 0)
        self.setpos(nextpos)
        self.savecol()

    def eof(self):
        nextpos = self.wnd.document.endpos()
        self.wnd.screen.locate(nextpos, middle=True)
        nextpos = self.adjust_nextpos(self.pos, nextpos)
        self.setpos(nextpos)
        self.savecol()

