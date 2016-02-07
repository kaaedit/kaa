class Cursor:

    def __init__(self, wnd):
        self.wnd = wnd
        self.pos = 0
        self.preferred_col = 0
        self.preferred_linecol = 0
        self.last_screenpos = (-1, -1)

    def refresh(self, top=None, middle=None, bottom=None,
                align_always=False):
        self.pos, y, x = self.wnd.locate_cursor(
            self.pos, top=top, middle=middle, bottom=bottom,
            align_always=align_always)
        assert self.pos is not None
        self.last_screenpos = (x, y)

    def setpos(self, pos, top=None, middle=None, bottom=None,
               align_always=False):
        assert pos is not None

        self.pos = pos
        self.refresh(top=top, middle=middle, bottom=bottom,
                     align_always=align_always)

    def savecol(self):
        """Update current preferred column"""

        y, x = self.wnd.screen.getrowcol(self.pos)
        self.preferred_col = x
        self.preferred_linecol = self.wnd.screen.get_cursorcol(self.pos)

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
            idx, prevrow = self.wnd.screen.getrow(row.posfrom - 1)
        else:
            idx -= 1

        pos = self.wnd.screen.get_pos_above(idx, self.preferred_col)
        pos = self.adjust_nextpos(self.pos, pos)
        self.setpos(pos)

        return True

    def down(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)
        idx, row = self.wnd.screen.getrow(self.pos)

        if self.wnd.screen.is_lastrow(row):
            return False

        if idx + 1 >= self.wnd.screen.portto:
            # Scroll down a line
            if not self.wnd.linedown():
                # last line of text file
                return False
            idx, nextrow = self.wnd.screen.getrow(row.posto)
        else:
            idx += 1

        pos = self.wnd.screen.get_pos_under(idx, self.preferred_col)
        pos = self.adjust_nextpos(self.pos, pos)
        self.setpos(pos)

        return True

    def prev_line(self):
        tol = self.wnd.document.gettol(self.pos)
        if tol != 0:
            self.wnd.screen.locate(tol - 1, top=True)

            prev = self.wnd.document.gettol(tol - 1)
            pos = self.wnd.screen.get_pos_at_cols(prev, self.preferred_linecol)
            pos = self.adjust_nextpos(self.pos, pos)
            self.wnd.screen.locate(pos, top=True)

            self.setpos(pos)
            return True

    def next_line(self):
        next = self.wnd.document.gettol(self.wnd.document.geteol(self.pos))
        if self.pos < next:
            self.wnd.screen.locate(next, bottom=True)

            pos = self.wnd.screen.get_pos_at_cols(next, self.preferred_linecol)
            pos = self.adjust_nextpos(self.pos, pos)
            self.wnd.screen.locate(pos, bottom=True)

            self.setpos(pos)
            return True

    def adjust_nextpos(self, curpos, nextpos):
        return nextpos

    def word_right_pos(self, pos):
        # Get next word break
        nextpos = self.wnd.document.endpos()
        for word in self.wnd.document.mode.split_word(pos):
            f, t, chars, cg = word
            nextpos = t
            if f == pos:  # first word
                # get next word
                continue
            if cg[0] == 'Z':  # skip white space
                continue
            nextpos = f
            break

        return self.adjust_nextpos(pos, nextpos)

    def word_left_pos(self, pos):
        # Get previous word break
        prevpos = tol = self.wnd.document.gettol(pos)
        if pos == prevpos:
            prevpos -= 1
        else:
            for f, t, chars, cg in self.wnd.document.mode.split_word(tol):
                #  This word is at after cursor pos
                if pos <= f:
                    break
                if cg[0] == 'Z':  # skip white space
                    continue
                prevpos = f

        return self.adjust_nextpos(pos, prevpos)

    def right(self, word=False):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        if self.pos == self.wnd.document.endpos():
            return

        if not word:
            # Get right of current position
            nextpos = self.wnd.document.get_nextpos(self.pos)
            nextpos = self.adjust_nextpos(self.pos, nextpos)
        else:
            nextpos = self.word_right_pos(self.pos)

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
            prevpos = self.adjust_nextpos(self.pos, prevpos)
        else:
            prevpos = self.word_left_pos(self.pos)

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

        lastrow = self.wnd.screen.rows[self.wnd.screen.portto - 1]
        if lastrow.posto == self.wnd.document.endpos():
            nextpos = self.adjust_nextpos(self.pos, lastrow.posto)
            if self.pos != lastrow.posto:
                self.setpos(nextpos)
                return True

        if self.wnd.pagedown():
            idx = max(0, min(self.wnd.screen.portto - 1,
                             self.wnd.screen.portfrom + y))
            pos = self.wnd.screen.get_pos_under(idx, self.preferred_col)

            nextpos = self.adjust_nextpos(self.pos, pos)
            self.setpos(nextpos)

            return True
        else:
            pos = self.wnd.document.endpos()
            nextpos = self.adjust_nextpos(self.pos, pos)
            if nextpos != pos:
                self.setpos(nextpos)
                return True

    def pageup(self):
        # Ensure current position is displayed
        self.wnd.screen.locate(self.pos, middle=True, align_always=False)

        idx, row = self.wnd.screen.getrow(self.pos)
        y = idx - self.wnd.screen.portfrom

        if self.wnd.pageup():
            idx = max(0, min(self.wnd.screen.portto - 1,
                             self.wnd.screen.portfrom + y))
            pos = self.wnd.screen.get_pos_above(idx, self.preferred_col)
            nextpos = self.adjust_nextpos(self.pos, pos)
            self.setpos(nextpos)

            return True
        elif self.pos != 0:
            nextpos = self.adjust_nextpos(self.pos, 0)
            if nextpos != self.pos:
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
            pos = row.posto - 1

        nextpos = self.adjust_nextpos(self.pos, pos)
        self.setpos(nextpos)
        self.savecol()

    def tol(self, pos):
        tol = self.wnd.document.gettol(pos)
        nextpos = self.adjust_nextpos(self.pos, tol)
        self.wnd.screen.locate(nextpos, middle=True)
        self.setpos(nextpos)
        self.savecol()

    def first_letter(self, pos):
        f, tol = self.wnd.document.mode.get_indent_range(pos)
        nextpos = self.adjust_nextpos(self.pos, tol)
        self.wnd.screen.locate(nextpos, middle=True)
        self.setpos(nextpos)
        self.savecol()

    def eol(self, pos):
        eol = self.wnd.document.get_line_to(pos)
        nextpos = self.adjust_nextpos(self.pos, eol)
        self.wnd.screen.locate(nextpos, middle=True)
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
