import re
import math
from unicodedata import east_asian_width

import kaa
from kaa import document
from kaa.document import is_combine


def calc_lineno_width(screen):
    if not screen.rows:
        return 0

    lineno = screen.document.buf.lineno.lineno(screen.rows[-1].posfrom)
    digits = int(math.log10(lineno) + 1)
    digits += 2     # one space left and right of line number.
    return digits


class Row:
    height = 1
    bgcolor = None

    def __init__(self, posfrom, tol, colfrom, wrapindent, chars, cols,
                 positions, intervals):
        self.posfrom = posfrom
        self.posto = positions[-1] + 1 if positions else posfrom
        self.colfrom = colfrom
        self.tol = tol
        self.wrapindent = wrapindent
        self.chars = chars
        self.cols = cols
        self.positions = positions
        self.intervals = intervals

    def get_char(self, pos):
        ret = []
        for p, c in zip(self.positions, self.chars):
            if p == pos:
                ret.append(c)
        return ''.join(ret)


def translate_chars(posfrom, chars, tab_width, ambiguous_width):
    """Build character informations from chars.

    Returns tuple of four lists. The first item is a list of characters to be
    displayed. Second item is a list of columns of each characters. Third item
    is a list of position in document of each characters. Last item is a list of
    interval from first column top of character of each character.
    """

    curcol = 0
    dispchrs = ''
    dispcols = []
    positions = []
    intervals = []
    double_width = set('WF')
    if ambiguous_width == 2:
        double_width.add('A')

    pos = posfrom
# return chars, [1]*len(chars), [(posfrom+i) for i in range(len(chars))],
# [0]*len(chars)

    for c in chars:
        if c == '\t':
            dispstr = ' ' * (tab_width - (curcol % tab_width))
        elif (((c != '\n') and (c < '\x20'))  # control chars
              or (c == '\x7f')                     # backspace
              or ('\ud800' <= c <= '\udfff')):     # surrogate pair
            dispstr = repr(c)[1:-1]
        else:
            dispstr = c

        dispchrs += dispstr
        for i, d in enumerate(dispstr):
            positions.append(pos)
            intervals.append(i)
            # first char of line never be combined
            if curcol and is_combine(c):
                cols = 0
            else:
                w = east_asian_width(d)
                cols = 2 if w in double_width else 1
            dispcols.append(cols)
            curcol += cols
        pos += 1

# return chars, [1]*len(chars), [(posfrom+i) for i in range(len(chars))],
# [0]*len(chars)
    return dispchrs, dispcols, positions, intervals


MIN_WRAPCOLS = 10


def col_splitter(maxcol, tol, dispchrs, dispcols, positions,
                 intervals, styles, stylemap, nowrap=False, nowrapindent=False):
    """Split string by column"""

    if nowrap:
        return [Row(tol, tol, 0, 0, dispchrs, dispcols, positions, intervals)]

    assert maxcol >= 2
    rowfrom = rowto = 0
    sumcols = 0
    wrappos = None
    sumcols_at_wrappos = 0

    posfrom = tol
    colfrom = 0
    wrapindent = 0

    ret = []

    for col in dispcols:

        if not col:
            rowto += 1
            continue

        # check if nowrap
        if rowfrom < rowto:
            wrappable = True

            if rowto < len(positions):

                curpos = positions[rowto - 1]
                nextpos = positions[rowto]

                tokenid = styles[curpos - tol]
                nexttokenid = styles[nextpos - tol]

                style = stylemap.get(tokenid, None)
                if style and style.nowrap:
                    nextstyle = stylemap.get(nexttokenid)
                    if nextstyle and nextstyle.nowrap:
                        wrappable = False

            if wrappable:
                wrappos = rowto
                sumcols_at_wrappos = sumcols

        if ((sumcols + col) >= (maxcol - wrapindent)) and (rowfrom != rowto):
            # do not split at newlines
            if (rowto >= len(dispchrs)) or (dispchrs[rowto] != '\n'):

                if wrappos is None:
                    # No wrappable position found. So, fill as many chars as we
                    # can.
                    wrappos = rowto
                    sumcols_at_wrappos = sumcols

                assert rowfrom != wrappos
                row = Row(
                    posfrom, tol, colfrom, wrapindent, dispchrs[
                        rowfrom:wrappos],
                    dispcols[rowfrom:wrappos], positions[
                        rowfrom:wrappos],
                    intervals[rowfrom:wrappos])

                ret.append(row)
                colfrom += sum(dispcols[rowfrom:wrappos])

                rowfrom = wrappos
                sumcols = sumcols - sumcols_at_wrappos

                wrappos = None
                sumcols_at_wrappos = None

                posfrom = row.posto

                # set wrap-indent width after second row
                if not nowrapindent and len(ret) == 1:
                    wrapindent = re.match(r' *', dispchrs).end()
                    if wrapindent + MIN_WRAPCOLS > maxcol:
                        wrapindent = max(0, maxcol - MIN_WRAPCOLS)

        sumcols += col
        rowto += 1

    if rowfrom != len(dispcols) or not dispchrs:
        row = Row(
            posfrom, tol, colfrom, wrapindent, dispchrs[
                rowfrom:], dispcols[rowfrom:],
            positions[rowfrom:], intervals[rowfrom:])
        ret.append(row)

    return ret


class Selection:

    def __init__(self, screen):
        self._marks = document.Marks()
        self.screen = screen
        self._rectangular = False
        self._linewise = False

    def _get_cursor_start(self):
        return self._marks.get('start', None)

    def _set_cursor_start(self, pos):
        self._marks['start'] = pos

    def _is_cursor_started(self):
        """Return True if range was selected"""

        return self._get_cursor_start() is not None

    def _get_cursor_end(self):
        return self._marks.get('end', None)

    def _set_end(self, pos):
        self._marks['end'] = pos

    def _set_mark(self, pos):
        self._marks['mark'] = pos

    def _get_mark(self):
        return self._marks.get('mark', None)

    def has_mark(self):
        return self._get_mark() is not None

    def is_selected(self):
        if self._is_cursor_started() or self.has_mark():
            sel = self.get_selrange()
            if sel:
                f, t, = sel
                return f != t

    def is_rectangular(self):
        return self._rectangular

    def set_mark(self, pos):
        cur = self.get_selrange()
        self._rectangular = False
        self._linewise = False

        if pos is not None:
            cursor_start = self._get_cursor_start()
            if cursor_start is not None:
                self._set_mark(cursor_start)
            else:
                self._set_mark(pos)
            self._set_cursor_start(None)
        else:
            self._set_mark(pos)

        if cur != self.get_selrange():
            self.screen.style_updated()
            return True

    def set_linewise_mark(self, pos):
        self.set_mark(pos)
        self.set_to(pos)
        self._linewise = True
        self.screen.style_updated()

    def set_rectangle_mark(self, pos):
        self.set_mark(pos)
        self._rectangular = True
        self._linewise = False

    def begin_cursor_sel(self, pos):
        """Start cursor range selection if it was not started"""

        if self.has_mark():
            return

        if self._is_cursor_started():
            return

        self._linewise = False
        self._rectangular = False
        self._set_cursor_start(pos)
        self._set_end(pos)

    def set_to(self, pos):
        """Update where selection to."""

        if not self.has_mark() and not self._is_cursor_started():
            return
        changed = self._get_cursor_end() != pos
        self._set_end(pos)

        if changed:
            self.screen.style_updated()

    def end_cursor_sel(self):
        """Clear selection"""

        changed = self._is_cursor_started()

        self._set_cursor_start(None)
        self._set_end(None)

        if changed:
            self.screen.style_updated()

    def clear(self):
        """Clear selection"""

        changed = self._is_cursor_started() is not None
        if not changed:
            changed = self._get_mark() is not None

        self._set_cursor_start(None)
        self._set_end(None)
        self._set_mark(None)
        self._linewise = False

        if changed:
            self.screen.style_updated()

    def get_selrange(self):
        start = self._get_cursor_start()
        if start is None:
            start = self._get_mark()

        end = self._get_cursor_end()
        if start is None or end is None:
            return None

        if not self._linewise:
            if start == end:
                return None
            return tuple(sorted((start, end)))

        if start < end:
            s = self.screen.document.gettol(start)
            e = self.screen.document.geteol(end)
        else:
            s = self.screen.document.gettol(end)
            e = self.screen.document.geteol(start)
        return (s, e)

    def set_range(self, f, t):
        self._rectangular = False
        self._linewise = False
        start = self._get_cursor_start()
        end = self._get_cursor_end()
        if (start, end) != (f, t):
            self._set_cursor_start(f)
            self._set_end(t)
            self._set_mark(None)
            self.screen.style_updated()

    def _calc_col(self, pos):
        tol = self.screen.document.gettol(pos)
        eol, s = self.screen.document.getline(tol)
        (dispchrs, dispcols, positions, intervals) = translate_chars(
            tol, s, self.screen.document.mode.tab_width,
            kaa.app.config.AMBIGUOUS_WIDTH)

        if pos < eol:
            n = positions.index(pos)
        else:
            n = len(dispcols)
        return tol, eol, sum(dispcols[0:n])

    def get_rect_range(self):
        sel = self.get_selrange()
        if not sel:
            return
        posfrom, _, col1 = self._calc_col(sel[0])
        _, posto, col2 = self._calc_col(sel[1])
        colfrom, colto = (col1, col2) if (col1 < col2) else (col2, col1)

        return posfrom, posto, colfrom, colto

    def get_col_string(self, tol, colfrom, colto):
        eol, s = self.screen.document.getline(tol)
        (dispchrs, dispcols, positions, intervals) = translate_chars(
            tol, s, self.screen.document.mode.tab_width,
            kaa.app.config.AMBIGUOUS_WIDTH)

        col = 0
        for top, c in enumerate(dispcols):
            if colfrom <= col:
                top -= intervals[top]
                break
            col += c
        else:
            return

        for end, c in enumerate(dispcols[top:]):
            if colto <= col:
                end = top + end
                end -= intervals[end]
                break
            col += c
        else:
            end = len(dispcols)

        toppos = positions[top] if top < len(dispcols) else eol
        endpos = positions[end] if end < len(dispcols) else eol
        return toppos, endpos, s[toppos - tol:endpos - tol]

    def on_document_updated(self, pos, inslen, dellen):
        self._marks.updated(pos, inslen, dellen)


class Screen:

    """
    Attributes:
        rows --  list of Row objects.

        portfrom, portto -- Index of portion of rows to be displayed
            on the screen.
    """

    def __init__(self):
        self._oninit()
        self.width = 2      # width of screen
        self.height = 1     # height of screen

    def _oninit(self):
        self.document = None
        self.nowrap = False

        # Rows displayed on screen
        # A row at self.rows[0] should be start from top
        # of document or from a top of physical line.
        # A row at self.rows[-1] should be finished at end
        # of document or an end of physical line.
        # An entire physical line will be stored in self.rows,
        # never be a part of physical line.
        self.rows = []
        self.portfrom = 0   # self.rows[self.portfrom:self.portto]
        # returns rows displayed on the screen.
        self.portto = 0
        self.pos = 0        # Position of top-left corner
        self.updated_pos = None
        self._style_updated = False
        self._need_redraw = False

        self.selection = Selection(self)

    def set_document(self, doc):
        self._oninit()

        self.document = doc
        self.nowrap = doc.mode.SCREEN_NOWRAP

    def close(self):
        self.document = self.selection = None

    def get_visible_rows(self):
        return self.rows[self.portfrom:self.portto]

    def get_visible_range(self):
        if not self.rows:
            return
        rows = self.get_visible_rows()
        if not rows:
            return -1, -1
        return (rows[0].posfrom, rows[-1].posto)

    def get_total_height(self, max_height):

        # build all rows
        ret = 0
        tol = 0
        while True:
            eol, s = self.document.getline(tol)
            styles = self.document.getstyles(tol, eol)
            rows = self._buildrow(tol, s, styles)
            tol = eol
            ret += sum(r.height for r in rows)
            if ret >= max_height:
                break
            if self.is_lastrow(rows[-1]):
                break

        return min(max_height, ret)

    def setsize(self, width, height):
        if self.width != width or self.height != height:
            self.width = max(2, width)
            self.height = max(1, height)
            if self.document:
                self.locate(self.pos, top=True, refresh=True)

    def _buildrow(self, pos, s, styles):
        dispchrs, dispcols, positions, intervals = translate_chars(
            pos, s, self.document.mode.tab_width,
            kaa.app.config.AMBIGUOUS_WIDTH)

        if self.document.mode.SHOW_LINENO:
            linenowidth = calc_lineno_width(self)
        else:
            linenowidth = 0

        nowrapindent = self.document.mode.NO_WRAPINDENT
        width = max(2, self.width - linenowidth)
        return col_splitter(width, pos, dispchrs, dispcols,
                            positions, intervals, styles, self.document.mode.stylemap, nowrap=self.nowrap, nowrapindent=nowrapindent)

    def on_document_updated(self, pos, inslen, dellen):
        self.selection.on_document_updated(pos, inslen, dellen)

        if not self.rows:
            return

        # calculate new top of screen position after update
        if pos > self.rows[-1].posto:
            # Nothing changed on screen
            return

        if self.updated_pos is None:
            self.updated_pos = self.rows[self.portfrom].posfrom

        if inslen >= dellen:
            if pos < self.updated_pos:
                self.updated_pos += inslen - dellen
        elif inslen < dellen:
            deleted = dellen - inslen
            if pos < self.updated_pos:
                if pos + deleted > self.updated_pos:
                    self.updated_pos = pos
                else:
                    tol = self.document.gettol(self.updated_pos - deleted)
                    if tol != self.document.gettol(pos):
                        # Position of top of screen is not changed
                        # if deleted on same physical line.
                        self.updated_pos -= deleted

        self.updated_pos = min(self.updated_pos, self.document.endpos())
        self.pos = min(self.pos, self.document.endpos())

    def style_updated(self):
        self._style_updated = True

    def apply_updates(self):
        if not self.rows:
            self.locate(0, top=True)
            return

        if self.updated_pos is not None:
            self.locate(self.updated_pos,
                        top=True, refresh=True)
        self.updated_pos = None

        if self._style_updated:
            self._need_redraw = True
            self._style_updated = False

    def is_row_updated(self):
        return self._need_redraw

    def row_drawn(self):
        self._need_redraw = False

    def is_lastrow(self, row):
        if row.posto == self.document.endpos():
            if not row.chars:
                return True
            if not row.chars[-1].endswith('\n'):
                return True

    def is_visible(self, pos):
        idx, col = self.getrowcol(pos)
        if idx == -1:
            return False
        return self.portfrom <= idx < self.portto

    def get_pos_under(self, rowidx, col):
        """Get pos at col of row when cursor downed from above row"""

        row = self.rows[rowidx]
        pos = self._getpos_fromrowcol(row, col)

        # Return next pos if the pos start at a row above
        if row.cols:
            if (row.positions[0] == pos) and (row.intervals[0] != 0):
                pos = self.document.get_nextpos(pos)

        return pos

    def get_pos_above(self, rowidx, col):
        """Get pos at col of row when cursor upped from below row"""

        row = self.rows[rowidx]
        pos = self._getpos_fromrowcol(row, col)

        # Return next pos if the pos start at a row above
        if row.cols:
            if (row.positions[0] == pos) and (row.intervals[0] != 0):
                nextpos = self.document.get_nextpos(pos)
                if nextpos < row.positions[-1]:
                    return nextpos

        return pos

    def _getpos_fromrowcol(self, row, col):
        """Returns position of specified column"""

        if not row.cols:
            return row.posfrom

        p = 0
        col = col - row.wrapindent
        for pos, charcols, c in zip(row.positions, row.cols, row.chars):
            if (p + charcols > col) or (c == '\n'):
                return pos
            p += charcols
        else:
            if self.is_lastrow(row):
                return row.posto
            else:
                ret = row.positions[-1]
                return ret

    def getrow(self, pos):
        assert pos is not None
        if self.rows and self.rows[0].posfrom <= pos:
            for i, row in enumerate(self.rows):
                if row.posfrom <= pos < row.posto:
                    return i, row
            if self.rows and self.is_lastrow(self.rows[-1]):
                return len(self.rows) - 1, self.rows[-1]

        return -1, None

    def getrowcol(self, pos):
        idx, row = self.getrow(pos)
        if idx == -1:
            return -1, -1
        else:
            try:
                col = row.positions.index(pos)
            except ValueError:
                col = len(row.positions)
            return idx, sum(c for c in row.cols[:col]) + row.wrapindent

    def get_cursorcol(self, pos):
        idx, row = self.getrow(pos)
        if idx == -1:
            return 0

        if row.cols:
            if pos == row.posto:
                cols = sum(row.cols)
            else:
                cols = sum(row.cols[:row.positions.index(pos)])
        else:
            cols = 0

        for n in range(idx - 1, -1, -1):
            nrow = self.rows[n]
            if nrow.tol != row.tol:
                return cols
            else:
                cols += sum(nrow.cols)

        return cols

    def get_pos_at_cols(self, tol, cols):
        posidx, row = self.getrow(tol)
        if not row:
            return tol

        p = 0
        for n in range(posidx, len(self.rows)):
            row = self.rows[n]
            if row.tol != tol:
                break

            for pos, charcols, c in zip(row.positions, row.cols, row.chars):
                if p + charcols > cols:
                    return pos
                p += charcols

        return self.document.get_line_to(tol)

    def _fillscreen(self):
        while True:
            bottomrow = self.rows[-1]
            if self.is_lastrow(bottomrow):
                break

            height = sum(row.height for row in self.rows[self.portfrom:])
            if height >= self.height:
                break

            eol, s = self.document.getline(bottomrow.posto)
            styles = self.document.getstyles(bottomrow.posto, eol)
            self.rows.extend(self._buildrow(bottomrow.posto, s, styles))

        # Update bottom of visible rows
        height = 0
        for i in range(self.portfrom, len(self.rows)):
            if height >= self.height:
                self.portto = i
                break
            height += self.rows[i].height
        else:
            self.portto = len(self.rows)

        # Remove unnecessary rows
        porttop = self.rows[self.portfrom].tol
        for i, row in enumerate(self.rows):
            if row.tol == porttop:
                del self.rows[0:i]
                self.portfrom -= i
                self.portto -= i
                break

        portend = self.rows[self.portto - 1].tol
        for i, row in enumerate(self.rows[self.portto:]):
            if row.tol != portend:
                del self.rows[self.portto + i:]
                break

    def locate(self, pos, top=False, middle=False, bottom=False,
               align_always=False, refresh=False):

        assert top or middle or bottom
        if self.updated_pos is not None:
            refresh = True
            self.updated_pos = None

        posidx = -1
        if not refresh:
            posidx, posrow = self.getrow(pos)

        if not refresh and (posidx != -1):
            if not align_always and (self.portfrom <= posidx < self.portto):
                return False

        else:
            # build specified row
            tol = self.document.gettol(pos)
            eol, s = self.document.getline(tol)
            styles = self.document.getstyles(tol, eol)
            self.rows = self._buildrow(tol, s, styles)
            posidx, posrow = self.getrow(pos)

        self._need_redraw = True
        self.vert_align(posidx, top, middle, bottom)

        return True

    def vert_align(self, rowidx, top=False, middle=False, bottom=False):
        assert top or middle or bottom
        # move the row to middle or bottom

        old_range = self.get_visible_range()
        targetrow = self.rows[rowidx]

        if top:
            rowbottom = 0
        elif middle:
            rowbottom = self.height // 2
        else:
            # bottom
            rowbottom = max(0, self.height - targetrow.height)

        if rowbottom > 0:
            # build rows above target row
            height = sum(row.height for row in self.rows[:rowidx + 1])

            while height <= rowbottom:
                curtop = self.rows[0].posfrom
                if curtop == 0:
                    # top of buffer
                    break

                # build previous line
                top = self.document.gettol(curtop - 1)
                eol, s = self.document.getline(top)
                styles = self.document.getstyles(top, eol)
                rows = self._buildrow(top, s, styles)
                height += sum(row.height for row in rows)
                rowidx += len(rows)

                self.rows[0:0] = rows

            # move row
            height = 0
            for n in range(rowidx, -1, -1):
                if height > rowbottom:
                    break
                row = self.rows[n]
                height += row.height
                rowidx = n

        self.portfrom = rowidx
        self.pos = self.rows[rowidx].posfrom

        self._fillscreen()

        ret = old_range != self.get_visible_range()
        if ret:
            self._need_redraw = True
        return ret

    def linedown(self):
        if self.portfrom < len(self.rows) - 1:
            self.portfrom += 1
            self.pos = self.rows[self.portfrom].posfrom
            self._fillscreen()
            self._need_redraw = True
            return True
        else:
            currow = self.rows[self.portfrom]
            if not self.is_lastrow(currow):
                self.locate(currow.posto, top=True)
                self._need_redraw = True
                return True
        return False

    def lineup(self):
        if self.portfrom > 0:
            self.portfrom -= 1
            self.pos = self.rows[self.portfrom].posfrom
            self._fillscreen()
            self._need_redraw = True
            return True

        elif self.pos > 0:
            tol = self.document.gettol(self.pos - 1)
            eol, s = self.document.getline(tol)
            styles = self.document.getstyles(tol, eol)
            rows = self._buildrow(tol, s, styles)
            self.rows[0:0] = rows
            self.pos = rows[-1].posfrom
            self.portfrom = len(rows) - 1
            self._fillscreen()
            self._need_redraw = True
            return True

        return False

    def pagedown(self):
        if self.height != 1:
            curpos = self.pos
            if self.rows[self.portto - 1].posto == self.document.endpos():
                if (self.portto - self.portfrom) > (self.height // 2):
                    self.vert_align(self.portto - 1, middle=True)
            else:
                self.vert_align(self.portto - 1, top=True)

            ret = self.pos != curpos
            if ret:
                self._need_redraw = True
            return ret
        else:
            return self.linedown()

    def pageup(self):
        if self.height != 1:
            curpos = self.pos
            self.vert_align(self.portfrom, bottom=True)
            ret = self.pos != curpos
            if ret:
                self._need_redraw = True
            return ret
        else:
            return self.lineup()
