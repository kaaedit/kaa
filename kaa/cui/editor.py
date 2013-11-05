import itertools, curses, curses.panel
from kaa.cui.wnd import Window
import kaa
import kaa.log
from kaa import screen, cursor
from kaa.cui.color import ColorName

class TextEditorWindow(Window):
    """Text editor window"""
    show_lineno = True
    splitter = None
    document = None
    statusbar = None
    editmode = None
    visible = True
    
    def _oninit(self):
        super()._oninit()
        self._cwnd.leaveok(0)
        self._cwnd.scrollok(0)

        self.screen = screen.Screen()
        self.screen.setsize(*self.getsize())
        self.cursor = cursor.Cursor(self)
        self.pending_str = ''
        self._drawn_rows = {}
        self.charattrs = {}

    def destroy(self):
        if self.document:
            self.document.del_window(self)
        self.screen.close()
        self.document = self.screen = self.cursor = None
        self.splitter = None
        self.statusbar = None

        super().destroy()

    def show_doc(self, doc):
        if doc is self.document:
            return

        if self.document:
            self.document.del_window(self)

        self._oninit()

        self.document = doc
        self.screen.set_document(doc)
        self.document.add_window(self)

        self._drawn_rows = {}
        self.draw_screen()
        self.refresh()
        self.cursor.refresh(middle=True)

    def set_editmode(self, mode):
        self.editmode = mode
        self.editmode.activated(self)

    def dup(self):
        ret = self.__class__(parent=self.parent)
        return ret

    def set_splitter(self, splitter):
        self.splitter = splitter

    def set_statusbar(self, statusbar):
        self.statusbar = statusbar

    def bring_top(self):
        if curses.panel.top_panel() is not self._panel:
            super().bring_top()

            self.draw_screen(force=True)

    def activate(self):
        super().activate()
        kaa.app.set_focus(self)

    def set_cursor(self, cursor):
        self.cursor = cursor

    def set_visible(self, visible):
        self.visible =  visible
        self.draw_screen(force=True)

    def _flush_pending_str(self):
        if self.editmode:
            return self.editmode.flush_pending_str(self)

    def _update_activeframe(self):
        frame = self.get_label('frame')
        if frame:
            frame.bring_top()
            frame.set_active_editor(self)

    def on_focus(self):
        super().on_focus()
        self._update_activeframe()

        if self.document:
            self.document.mode.on_focus(self)

    def _getcharattrs(self, row, rectangular, selfrom, selto, colfrom, colto):
        # returns character attributes of each characters in row.
        ncols = row.colfrom
        for pos, cols in zip(row.positions, row.cols):
            attr = 0
            sel = False
            if selfrom <= pos < selto:
                if rectangular:
                    if colfrom <= ncols < colto:
                        sel = True
                    else:
                        sel = False
                else:
                    sel = True

            if sel:
                attr = curses.A_REVERSE

            color = kaa.app.colors.get_color(
                ColorName.DEFAULT,
                ColorName.DEFAULT)

            tokenid = self.charattrs.get(pos, None)
            if tokenid is None:
                tokenid = self.document.styles.getints(pos, pos+1)[0]

            style = self.document.mode.get_style(tokenid)
            color = style.cui_colorattr
            if style.underline:
                color += curses.A_UNDERLINE
            if style.bold:
                color += curses.A_BOLD

            yield (color + attr, style.rjust)

            ncols += cols
            
    def draw_screen(self, force=False):
        try:
            self._draw_screen(force=force)
        except curses.error:
            kaa.log.debug('error on drawing: {}'.format(self), exc_info=True)

    def _draw_screen(self, force=False):
        frame = self.get_label('frame')
        if frame:
            if kaa.app.get_activeframe() is not frame:
                return

        self.screen.apply_updates()
        if kaa.app.focus:
            if self.document.mode.is_cursor_visible():
                cury, curx = kaa.app.focus._cwnd.getyx()

        h, w = self._cwnd.getmaxyx()

        rows = list(self.screen.get_visible_rows())
        cur_sel = self.screen.selection.get_selrange()

        theme = self.document.mode.theme
        defaultcolor = theme.get_style('default').cui_colorattr

        if force or not self.visible:
            drawn = {}
            updated = True
        else:
            updated = len(rows) != len(self._drawn_rows)
            drawn = self._drawn_rows
        self._drawn_rows = {}

        tol = rows[0].tol
        lineno_width = 0
        if self.document.mode.SHOW_LINENO:
            lineno_color = self.document.mode.theme.get_style('lineno').cui_colorattr
            lineno_width = screen.calc_lineno_width(self.screen)
            lineno = self.document.buf.lineno.lineno(self.screen.pos)
        
        _, cursorrow = self.screen.getrow(self.cursor.pos)


        rectangular = self.screen.selection.is_rectangular()
        selfrom = selto = colfrom = colto = -1

        if not rectangular:
            selrange = self.screen.selection.get_selrange()
            if selrange:
                selfrom, selto = selrange
        else:
            selrect = self.screen.selection.get_rect_range()
            if selrect:
                selfrom, selto, colfrom, colto = selrect
        
        for n, row in enumerate(rows):
            if n > h:
                break
            if drawn.get(row) == (n, cur_sel):
                # The raw was already drawn.
                continue
            
            is_cursorline = row is cursorrow
            updated = True
            s = 0

            # clear row
            self._cwnd.move(n, 0)
            self._cwnd.clrtoeol()
            self._cwnd.chgat(n, 0, -1, defaultcolor)

            if not self.visible:
                continue

            # draw line no
            if self.document.mode.SHOW_LINENO:
                self._cwnd.move(n, 0)
                if tol != row.tol:
                    lineno += 1
                    tol = row.tol

                if row.posfrom == row.tol:
                    self.add_str(str(lineno).rjust(lineno_width-1), lineno_color)
                else:
                    self.add_str(' ' * (lineno_width-1), lineno_color)

                self.add_str(' ', defaultcolor)

            # move cursor to top of row
            self._cwnd.move(n, row.wrapindent+lineno_width)
            rjust = False

            for (attr, attr_rjust), group in itertools.groupby(
                    self._getcharattrs(row, rectangular, selfrom, selto, colfrom, colto)):

                if is_cursorline and self.document.mode.HIGHLIGHT_CURSORLINE:
                    attr |= curses.A_BOLD
                    
                if not rjust and attr_rjust:
                    rjust = True

                    rest = sum(row.cols[s:])
                    cy, cx = self._cwnd.getyx()
                    self._cwnd.move(cy, w-rest)

                slen = len(tuple(group))
                letters = ''.join(row.chars[s:s+slen]).rstrip('\n')
                self.add_str(letters, attr)
                s += slen

            if row.chars == '\n':
                if selfrom <= row.posfrom < selto:
                    if not rectangular or (colfrom == 0):
                        self.add_str(' ', curses.A_REVERSE)
            
            self._drawn_rows[row] = (n, cur_sel)

        if len(rows) < h:
            self._cwnd.move(len(rows), 0)
            self._cwnd.clrtobot()

        if kaa.app.focus:
            if self.document.mode.is_cursor_visible():
                kaa.app.focus._cwnd.move(cury, curx)

        return updated

    def on_document_updated(self, pos, inslen, dellen):
        self.screen.on_document_updated(pos, inslen, dellen)
        endpos = self.document.endpos()
        if self.cursor.pos > endpos:
            self.cursor.pos = endpos

    def style_updated(self, posfrom, posto):
        f, t = self.screen.get_visible_range()
        if posfrom <= t and f <= posto:
            self.screen.style_updated()
            updated = self.screen.apply_updates()
            if updated:
                self.draw_screen(force=True)
                self.refresh()

    CURSOR_TO_MIDDLE_ON_SCROLL = True
    def locate_cursor(self, pos, top=None, middle=None, bottom=None):

        if top is middle is bottom is None:
            middle = self.CURSOR_TO_MIDDLE_ON_SCROLL
            bottom = not self.CURSOR_TO_MIDDLE_ON_SCROLL

        updated = self.screen.apply_updates()
        self.screen.locate(pos, top=top, middle=middle, bottom=bottom)

        idx, x = self.screen.getrowcol(pos)
        y = idx - self.screen.portfrom

        retpos = self.screen.get_pos_under(idx, x)

        screenx = x
        if self.document.mode.SHOW_LINENO:
            screenx = x + screen.calc_lineno_width(self.screen)

        if (y, screenx) != self._cwnd.getyx():
            h, w = self._cwnd.getmaxyx()
            if y < h and screenx < w and y >=0 and screenx >= 0:
                self._cwnd.move(y, screenx)

        self.document.mode.on_cursor_located(self, retpos, y, x)
        return retpos, y, x

    def get_cursor_loc(self):
        y, x = self._cwnd.getyx()
        u, l = self._cwnd.getbegyx()
        return u+y, x+l
        
    def linedown(self):
        if self.screen.linedown():
            self.draw_screen()
            self.refresh()
            return True

    def lineup(self):
        if self.screen.lineup():
            self.draw_screen()
            self.refresh()
            return True

    def pagedown(self):
        if self.screen.pagedown():
            self.draw_screen()
            self.refresh()
            return True

    def pageup(self):
        if self.screen.pageup():
            self.draw_screen()
            self.refresh()
            return True

    def on_setrect(self, l, t, r, b):
        self._drawn_rows = {}
        if self.document:
            w = max(2, r-l)
            h = max(1, b-t)
            self.screen.setsize(w, h)
            self.draw_screen()
            self.cursor.setpos(self.cursor.pos) # relocate cursor
            self.cursor.savecol()

            self.refresh()

    def update_window(self):
        # if this editor is a part of ChildFrame,
        # update only if the ChildFrame is active.
        frame = self.get_label('frame')
        if frame:
            if kaa.app.get_activeframe() is not frame:
                return

        self.screen.apply_updates()
        if self.draw_screen():
            self.refresh()
            self.cursor.refresh()
            return True

    def on_killfocus(self):
        self._drawn_rows = {}
        self._flush_pending_str()

    def on_idle(self):
        if not self.closed:
            if self._flush_pending_str():
                return True

            if self.document.mode.update_charattr(self):
                return True

            return self.update_status()

    def update_status(self):
        if self.statusbar:
            modified = False
            if self.document.undo:
                if self.document.undo.is_dirty():
                    modified = True

            linecount = self.document.buf.lineno.linecount()
            lineno = self.document.buf.lineno.lineno(self.cursor.pos)
            col = self.screen.get_cursorcol(self.cursor.pos)
            updated = self.statusbar.set_info(
                filename=self.document.get_title(),
                modified=modified,
                lineno=lineno,
                col=col+1,
                linecount=linecount,
                editmode=self.editmode.MODENAME,
            )

            return updated

