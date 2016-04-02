import itertools
import curses
import curses.panel
from kaa.cui.wnd import Window
import kaa
import kaa.log
from kaa import screen, cursor


class TextEditorWindow(Window):

    """Text editor window"""

    OVERLAY_CURSORROW = 'cursor-row'  # Name of overlay style of theme

    show_lineno = True
    splitter = None
    document = None
    statusbar = None
    editmode = None
    visible = True
    highlight_cursor_row = False
    _command_repeat = 1

    def _oninit(self):
        super()._oninit()

        self._cwnd.leaveok(0)
        self._cwnd.scrollok(0)

        self.screen = screen.Screen()
        self.screen.setsize(*self.getsize())
        self.cursor = cursor.Cursor(self)
        self.pending_str = ''
        self.charattrs = {}
        self.highlight_cursor_row = False
        self.line_overlays = {}

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

        self.draw_screen()
        self.refresh()
        self.cursor.refresh(middle=True)

        kaa.app.set_idlejob()  # Reschedule idle procs

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

    def set_highlight_cursor_row(self, f):
        ret = f != self.highlight_cursor_row
        self.highlight_cursor_row = f
        if ret:
            self.refresh()
        return ret

    def set_line_overlay(self, pos, overlay=None):
        if overlay is not None:
            if self.line_overlays.get(pos, '') != overlay:
                self.line_overlays[pos] = overlay
                self.screen.style_updated()
                return True
        else:
            if pos in self.line_overlays:
                del self.line_overlays[pos]
                self.screen.style_updated()
                return True

    def clear_line_overlay(self):
        if self.line_overlays:
            self.line_overlays = {}
            self.screen.style_updated()

#    def bring_top(self):
#        if curses.panel.top_panel() is not self._panel:
#            super().bring_top()
#
#            self.draw_screen(force=True)

    def activate(self):
        super().activate()
        kaa.app.set_focus(self)

    def set_cursor(self, cursor):
        self.cursor = cursor

    def set_visible(self, visible):
        self.visible = visible
        self.draw_screen(force=True)

    def _flush_pending_str(self):
        if self.editmode:
            return self.editmode.flush_pending_str(self)

    def _update_activeframe(self):
        frame = self.get_label('frame')
        if frame:
            frame.bring_top()
            frame.set_active_editor(self)
            # bring frame to the top of frame list
            frame.mainframe.register_childframe(frame)

    def on_focus(self):
        super().on_focus()
        self._update_activeframe()

        if self.document:
            self.document.mode.on_focus(self)

    def _getcharattrs(self, row, rectangular, selfrom,
                      selto, colfrom, colto, line_overlay):
        # returns character attributes of each characters in row.

        ret = []
        if not row.positions:
            return ret

        posfrom = row.positions[0]
        styles = self.document.styles.getints(posfrom, row.positions[-1] + 1)

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

            tokenid = self.charattrs.get(pos, None)
            if tokenid is None:
                tokenid = styles[pos - posfrom]

            style = self.document.mode.get_style(tokenid)
            color = None
            if line_overlay:
                color = style.cui_overlays.get(line_overlay, None)
            if color is None:
                color = style.cui_colorattr

            if style.underline:
                color += curses.A_UNDERLINE
            if style.bold:
                color += curses.A_BOLD

            ret.append((color + attr, style.rjust))

            ncols += cols
        return ret

    def draw_screen(self, force=False):
        try:
            self._draw_screen(force=force)
        except curses.error:
            kaa.log.debug('error on drawing: {}'.format(self), exc_info=True)

    def _draw_screen(self, force=False):
        # don't draw is frame is not visible.
        frame = self.get_label('frame')
        if frame:
            if kaa.app.get_activeframe() is not frame:
                return

        self.screen.apply_updates()
        self.screen.row_drawn()

        # save cursor position
#        if kaa.app.focus:
#            if self.document.mode.is_cursor_visible():
#                cury, curx = kaa.app.focus._cwnd.getyx()
#
        h, w = self._cwnd.getmaxyx()

        rows = list(self.screen.get_visible_rows())

        lineno_width = 0
        lineno = self.document.buf.lineno.lineno(self.screen.pos)
        if self.document.mode.SHOW_LINENO:
            lineno_color = self.document.mode.theme.get_style(
                'lineno').cui_colorattr
            lineno_width = screen.calc_lineno_width(self.screen)

        _, cursorrow = self.screen.getrow(self.cursor.pos)

        tol = rows[0].tol
        eol = self.document.geteol(tol)
        endpos = self.document.endpos()

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

        theme = self.document.mode.theme
        defaultcolor = theme.get_style('default').cui_colorattr

        overlays = self.document.mode.get_line_overlays()
        overlays.update(self.line_overlays)

        for n, row in enumerate(rows):
            if n > h:
                break

            if tol != row.tol:
                tol = row.tol
                eol = self.document.geteol(tol)

            # check fillrow
            fill_row_attr = None
            if tol < eol:
                token_id = self.document.styles.getints(tol, tol+1)[0]
                tol_style = self.document.mode.get_style(token_id)
                if tol_style.fillrow:
                    fill_row_attr = tol_style.cui_colorattr

            line_overlay = None
            if row is cursorrow and (
                    self.highlight_cursor_row or
                    self.document.mode.HIGHLIGHT_CURSOR_ROW):

                line_overlay = self.OVERLAY_CURSORROW
            else:
                for pos in overlays.keys():
                    if (tol <= pos < eol) or (pos == tol == eol == endpos):
                        line_overlay = overlays[pos]
                        break

            # clear row
            self._cwnd.move(n, 0)
            self._cwnd.clrtoeol()

            erase_attr = defaultcolor
            if line_overlay:
                style = theme.get_style('default')
                erase_attr = style.cui_overlays.get(line_overlay, defaultcolor)
            elif fill_row_attr:
                erase_attr = fill_row_attr
            self._cwnd.chgat(n, 0, -1, erase_attr)

            if not self.visible:
                continue

            # draw line no
            if self.document.mode.SHOW_LINENO:
                self._cwnd.move(n, 0)

                if row.posfrom == row.tol:
                    self.add_str(str(lineno).rjust(lineno_width - 1),
                                 lineno_color)
                else:
                    self.add_str(' ' * (lineno_width - 1), lineno_color)

                self.add_str(' ', defaultcolor)

            # increment line no
            lineno += 1

            # move cursor to top of row
            self._cwnd.move(n, row.wrapindent + lineno_width)

            rjust = False
            spos = 0

            for (attr, attr_rjust), group in itertools.groupby(
                    self._getcharattrs(row, rectangular, selfrom, selto,
                                       colfrom, colto, line_overlay)):

                if not rjust and attr_rjust:
                    rjust = True

                    rest = sum(row.cols[spos:])
                    cy, cx = self._cwnd.getyx()
                    self._cwnd.move(cy, max(0, w - rest))

                slen = len(tuple(group))
                letters = ''.join(row.chars[spos:spos + slen]).rstrip('\n')
                self.add_str(letters, attr)
                spos += slen

            if row.chars == '\n':
                if selfrom <= row.posfrom < selto:
                    if not rectangular or (colfrom == 0):
                        self.add_str(' ', curses.A_REVERSE)

        if len(rows) < h:
            self._cwnd.move(len(rows), 0)
            self._cwnd.clrtobot()

            if self.document.mode.SHOW_BLANK_LINE:
                attr = theme.get_style('blank-line-header').cui_colorattr
                for i in range(len(rows), h):
                    self._cwnd.move(i, 0)
                    self.add_str('~', attr)

#        if kaa.app.focus:
#            if self.document.mode.is_cursor_visible():
#                kaa.app.focus._cwnd.move(cury, curx)
        return

    def on_document_updated(self, pos, inslen, dellen):
        self.screen.on_document_updated(pos, inslen, dellen)
        endpos = self.document.endpos()
        if self.cursor.pos > endpos:
            self.cursor.pos = endpos

    def style_updated(self, posfrom, posto):
        f, t = self.screen.get_visible_range()
        if posfrom <= t and f <= posto:
            self.screen.style_updated()

    CURSOR_TO_MIDDLE_ON_SCROLL = True

    def locate_cursor(self, pos, top=None, middle=None, bottom=None,
                      align_always=False):

        if top is middle is bottom is None:
            middle = self.CURSOR_TO_MIDDLE_ON_SCROLL
            bottom = not self.CURSOR_TO_MIDDLE_ON_SCROLL

        self.screen.apply_updates()
        self.screen.locate(pos, top=top, middle=middle, bottom=bottom,
                           align_always=align_always)

        idx, x = self.screen.getrowcol(pos)
        y = idx - self.screen.portfrom

        retpos = self.screen.get_pos_under(idx, x)

        screenx = x
        if self.document.mode.SHOW_LINENO:
            screenx = x + screen.calc_lineno_width(self.screen)

#        if (y, screenx) != self._cwnd.getyx():
#            h, w = self._cwnd.getmaxyx()
#            if y < h and screenx < w and y >= 0 and screenx >= 0:
#                self._cwnd.move(y, screenx)

        self.document.mode.on_cursor_located(self, retpos, y, x)
        if self.document.mode.HIGHLIGHT_CURSOR_ROW:
            self.screen.style_updated()

        return retpos, y, screenx

    def get_cursor_loc(self):
        y, x = self._cwnd.getyx()
        u, l = self._cwnd.getbegyx()
        return u + y, x + l

    def linedown(self):
        if self.screen.linedown():
            self._cwnd.scrollok(True)
            try:
                self._cwnd.scroll(1)
            finally:
                self._cwnd.scrollok(False)

            self.refresh()
            return True

    def lineup(self):
        if self.screen.lineup():
            self._cwnd.scrollok(True)
            try:
                self._cwnd.scroll(-1)
            finally:
                self._cwnd.scrollok(False)

            return True

    def pagedown(self):
        if self.screen.pagedown():
            return True

    def pageup(self):
        if self.screen.pageup():
            return True

    def on_setrect(self, l, t, r, b):
        if self.document:
            w = max(2, r - l)
            h = max(1, b - t)
            self.screen.setsize(w, h)
            self.draw_screen()
            self.cursor.setpos(self.cursor.pos)  # relocate cursor
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
        if self.screen.is_row_updated():
            if self.draw_screen():
                self.cursor.refresh()
                self.refresh()
                return True

    def on_killfocus(self):
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
                col=col + 1,
                linecount=linecount,
                editmode=self.editmode.MODENAME,
            )
            return updated

    def set_command_repeat(self, n):
        self._command_repeat = n

    def get_command_repeat(self):
        return self._command_repeat
