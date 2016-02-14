import unicodedata
import kaa
from kaa.command import Commands
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa import document
from kaa.filetype.default import modebase
from kaa import doc_re


class CursorCommands(Commands):

    @commandid('cursor.right')
    @norerun
    def right(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        if wnd.screen.selection.has_mark():
            for i in range(wnd.get_command_repeat()):
                wnd.cursor.right()
        elif wnd.screen.selection.is_selected():
            selrange = wnd.screen.selection.get_selrange()
            if wnd.cursor.pos > selrange[1]:
                wnd.cursor.right()
            else:
                wnd.cursor.setpos(wnd.cursor.adjust_nextpos(
                    wnd.cursor.pos, selrange[1]))
        else:
            for i in range(wnd.get_command_repeat()):
                wnd.cursor.right()

        wnd.screen.selection.end_cursor_sel()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.right.select')
    @norerun
    def right_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.right()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.left')
    @norerun
    def left(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        if wnd.screen.selection.has_mark():
            for i in range(wnd.get_command_repeat()):
                wnd.cursor.left()
        elif wnd.screen.selection.is_selected():
            selrange = wnd.screen.selection.get_selrange()
            if wnd.cursor.pos < selrange[0]:
                wnd.cursor.left()
            else:
                wnd.cursor.setpos(wnd.cursor.adjust_nextpos(
                    wnd.cursor.pos, selrange[0]))
        else:
            for i in range(wnd.get_command_repeat()):
                wnd.cursor.left()

        wnd.screen.selection.end_cursor_sel()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.left.select')
    @norerun
    def left_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        wnd.cursor.left()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.up')
    @norerun
    def up(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.up()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.up.select')
    @norerun
    def up_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.up()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.down')
    @norerun
    def down(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.down()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.down.select')
    @norerun
    def down_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.down()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.prev-line')
    @norerun
    def prev_line(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.prev_line()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.next-line')
    @norerun
    def next_line(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.next_line()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.word-right')
    @norerun
    def word_right(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.right(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.word-right.select')
    @norerun
    def word_right_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.right(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.word-left')
    @norerun
    def word_left(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.left(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.word-left.select')
    @norerun
    def word_left_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.left(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.pagedown')
    @norerun
    def pagedown(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.pagedown()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.pagedown.select')
    @norerun
    def pagedown_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.pagedown()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.pageup')
    @norerun
    def pageup(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.pageup()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.pageup.select')
    @norerun
    def pageup_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.pageup()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.home')
    @norerun
    def home(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.home()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.home.select')
    @norerun
    def home_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        wnd.cursor.home()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.end')
    @norerun
    def end(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.end()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.end.select')
    @norerun
    def end_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        wnd.cursor.end()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.top-of-line')
    @norerun
    def tol(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.tol(wnd.cursor.pos)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.first-letter-of-line')
    @norerun
    def first_letter(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.first_letter(wnd.cursor.pos)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.end-of-line')
    @norerun
    def eol(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.eol(wnd.cursor.pos)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.top-of-file')
    @norerun
    def top(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.tof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.top-of-file.select')
    @norerun
    def top_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        wnd.cursor.tof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.end-of-file')
    @norerun
    def last(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.end_cursor_sel()
        wnd.cursor.eof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.end-of-file.select')
    @norerun
    def last_select(self, wnd):
        wnd.document.mode.cancel_auto_indent(wnd)
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)
        wnd.cursor.eof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('cursor.go-to-line')
    @norerun
    @norec
    def go_to_line(self, wnd):
        def callback(w, s):
            s = s.strip()
            try:
                lineno = int(s)
            except ValueError as e:
                kaa.app.messagebar.set_message(str(e))
                return

            if lineno == 0 or lineno > wnd.document.buf.lineno.linecount():
                kaa.app.messagebar.set_message('Enter valid line number.')
                return

            wnd.document.mode.cancel_auto_indent(wnd)
            wnd.screen.selection.end_cursor_sel()

            pos = wnd.document.get_lineno_pos(lineno)
            tol = wnd.document.gettol(pos)
            wnd.cursor.setpos(wnd.cursor.adjust_nextpos(wnd.cursor.pos, tol))

        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Line number:', callback,
                                                filter=inputlinemode.number_filter)
        kaa.app.messagebar.set_message("Enter line number")

        kaa.app.show_dialog(doc)


class SelectionCommands(Commands):

    @commandid('selection.begin-cursor')
    @norerun
    def selection_begin(self, wnd):
        wnd.screen.selection.begin_cursor_sel(wnd.cursor.pos)

    @commandid('selection.set-to')
    @norerun
    def selection_set_end(self, wnd):
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @commandid('selection.end-cursor')
    @norerun
    def selection_clear(self, wnd):
        wnd.screen.selection.end_cursor_sel()

    @commandid('selection.set-mark')
    @norerun
    def selection_set_mark(self, wnd):
        if not wnd.screen.selection.has_mark():
            wnd.screen.selection.set_mark(wnd.cursor.pos)
        else:
            wnd.screen.selection.set_mark(None)

    @commandid('selection.set-linewise-mark')
    @norerun
    def selection_set_linewisemark(self, wnd):
        wnd.screen.selection.set_linewise_mark(wnd.cursor.pos)

    @commandid('selection.set-rectangle-mark')
    @norerun
    def selection_set_rectangle_mark(self, wnd):
        if not wnd.screen.selection.has_mark():
            wnd.screen.selection.set_rectangle_mark(wnd.cursor.pos)
        else:
            wnd.screen.selection.set_rectangle_mark(None)

    @commandid('selection.all')
    @norerun
    def select_all(self, wnd):
        f = wnd.cursor.adjust_nextpos(wnd.cursor.pos, 0)
        t = wnd.cursor.adjust_nextpos(wnd.cursor.pos, wnd.document.endpos())
        wnd.screen.selection.set_range(f, t)

    @commandid('selection.curline')
    @norerun
    def select_cur_line(self, wnd):
        tol = wnd.cursor.adjust_nextpos(
            wnd.cursor.pos,
            wnd.document.gettol(wnd.cursor.pos))
        eol = wnd.cursor.adjust_nextpos(
            wnd.cursor.pos,
            wnd.document.geteol(tol))

        wnd.screen.selection.set_range(tol, eol)

    @commandid('selection.curword')
    @norerun
    def select_cur_word(self, wnd):
        ret = wnd.document.mode.get_word_at(wnd.cursor.pos)
        if ret:
            f, t, cg = ret
            f = wnd.cursor.adjust_nextpos(wnd.cursor.pos, f)
            t = wnd.cursor.adjust_nextpos(wnd.cursor.pos, t)

            wnd.screen.selection.set_range(f, t)
            wnd.cursor.setpos(t)

    @commandid('selection.expand-sel')
    @norerun
    @norec
    def expand_sel(self, wnd):
        keys = wnd.editmode.last_command_keys
        L = len(keys)

        if L >= 3 and keys[-1] == keys[-2] == keys[-3]:
            self.select_all(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(1, self.select_all)

        elif L >= 2 and (keys[-1] == keys[-2]):
            self.select_cur_line(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(1, self.select_cur_line)

        else:
            self.select_cur_word(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(1, self.select_cur_word)

    @commandid('selection.line.begin')
    @norerun
    def lineselection_begin(self, wnd):
        tol = wnd.cursor.adjust_nextpos(
            wnd.cursor.pos, wnd.document.gettol(wnd.cursor.pos))
        wnd.screen.selection.begin_cursor_sel(tol)

    @commandid('selection.line.set-end')
    @norerun
    def lineselection_set_end(self, wnd):
        f = wnd.screen.get_start()
        if f is None:
            self.select_cur_line(wnd)
        else:
            pos = wnd.cursor.pos
            if pos < f:
                tol = wnd.cursor.adjust_nextpos(
                    wnd.document.gettol(pos))
                wnd.screen.selection.set_end(tol)
            else:
                eol = wnd.cursor.adjust_nextpos(
                    wnd.document.geteol(pos))
                wnd.screen.selection.set_end(eol)


class EditCommands(Commands):

    def delete_sel(self, wnd):
        if wnd.screen.selection.is_selected():
            if not wnd.screen.selection.is_rectangular():
                sel = wnd.screen.selection.get_selrange()
                wnd.screen.selection.clear()
                if sel:
                    f, t = sel
                    wnd.document.mode.delete_string(wnd, f, t)
                    return True
            else:
                return self._delete_rect_sel(wnd)

    def _delete_rect_sel(self, wnd):
        with wnd.document.undo_group():
            (posfrom, posto, colfrom, colto
             ) = wnd.screen.selection.get_rect_range()

            while posfrom < posto:
                sel = wnd.screen.selection.get_col_string(
                    posfrom, colfrom, colto)
                if sel:
                    f, t, org = sel
                    if org.endswith('\n'):
                        t = max(f, t - 1)
                    wnd.document.mode.delete_string(wnd, f, t)
                    posto -= (t - f)
                posfrom = wnd.document.geteol(posfrom)

            return True

    @commandid('edit.delete')
    def delete(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = nextpos = wnd.cursor.pos
        for i in range(wnd.get_command_repeat()):
            nextpos = wnd.document.get_nextpos(nextpos)

        nextpos = wnd.cursor.adjust_nextpos(pos, nextpos)
        if pos < nextpos:
            wnd.document.mode.delete_string(wnd, pos, nextpos)

    @commandid('edit.delete.word')
    def delete_word(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.right(word=True)

        nextpos = wnd.cursor.pos
        if pos < nextpos:
            wnd.document.mode.delete_string(wnd, pos, nextpos)

    @commandid('edit.delete.line')
    def delete_line(self, wnd):
        pos = wnd.cursor.pos
        nextpos = wnd.cursor.adjust_nextpos(
            pos, wnd.document.get_line_to(pos))
        if pos < nextpos:
            wnd.document.mode.delete_string(wnd, pos, nextpos)

    @commandid('edit.delete.currentline')
    def delete_currentline(self, wnd):
        pos = wnd.cursor.pos
        f = t = wnd.cursor.adjust_nextpos(pos, wnd.document.gettol(pos))
        for i in range(wnd.get_command_repeat()):
            t = wnd.cursor.adjust_nextpos(pos, wnd.document.geteol(t))

        if f < t:
            wnd.document.mode.delete_string(wnd, f, t)

    @commandid('edit.backspace')
    def backspace(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = prevpos = wnd.cursor.pos
        for i in range(wnd.get_command_repeat()):
            prevpos = wnd.cursor.adjust_nextpos(
                pos, wnd.document.get_prevpos(prevpos))

        if prevpos < pos:
            if pos == wnd.screen.pos:
                # locate cursor before delete to scroll half page up
                wnd.cursor.setpos(prevpos)

            wnd.document.mode.delete_string(wnd, prevpos, pos)

    @commandid('edit.backspace.word')
    def backspace_word(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        for i in range(wnd.get_command_repeat()):
            wnd.cursor.left(word=True)

        prevpos = wnd.cursor.pos
        if prevpos < pos:
            if prevpos < wnd.screen.pos:
                # locate cursor before delete to scroll half page up
                wnd.cursor.setpos(prevpos)

            wnd.document.mode.delete_string(wnd, prevpos, pos)

    @commandid('edit.newline')
    @norerun
    def newline(self, wnd):
        if not wnd.document.mode.auto_indent:
            wnd.document.mode.put_string(wnd, '\n')
            wnd.screen.selection.clear()
            return

        wnd.screen.selection.clear()
        wnd.document.mode.on_auto_indent(wnd)

    def _indent_line(self, wnd, pos):
        mode = wnd.document.mode
        f, t = mode.get_indent_range(pos)
        if pos > t:
            wnd.document.mode.put_string(wnd, '\t')
            wnd.screen.selection.clear()
            return

        if f != t:
            cols = mode.calc_cols(f, t)
        else:
            cols = 0

        s = mode.build_indent_str(cols + mode.indent_width)
        mode.replace_string(wnd, f, t, s, True)

    @commandid('edit.indent')
    def indent(self, wnd):
        if not wnd.screen.selection.is_selected():
            self._indent_line(wnd, wnd.cursor.pos)
            return

        for i in range(wnd.get_command_repeat()):
            doc = wnd.document
            tol, eol = doc.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)

            with wnd.document.undo_group():
                mode = wnd.document.mode
                while tol < wnd.screen.selection.get_selrange()[1]:
                    f, t = mode.get_indent_range(tol)
                    if f != t:
                        cols = mode.calc_cols(f, t)
                    else:
                        cols = 0

                    endpos = doc.endpos()
                    eol = doc.geteol(tol)

                    if (t + 1 < eol != endpos) or (t < eol == endpos):
                        s = mode.build_indent_str(cols + mode.indent_width)
                        mode.replace_string(wnd, f, t, s, False)
                        tol = eol + (len(s) - (t - f))
                    else:
                        tol = eol

        f, t = wnd.screen.selection.get_selrange()
        wnd.cursor.setpos(f)
        wnd.cursor.savecol()

    def _dedent_line(self, wnd, pos):
        mode = wnd.document.mode
        f, t = mode.get_indent_range(pos)
        if f != t:
            cols = mode.calc_cols(f, t)
        else:
            cols = 0

        s = mode.build_indent_str(max(0, cols - mode.indent_width))
        mode.replace_string(wnd, f, t, s, True)

    @commandid('edit.dedent')
    def dedent(self, wnd):
        if not wnd.screen.selection.is_selected():
            self._dedent_line(wnd, wnd.cursor.pos)
            return

        for i in range(wnd.get_command_repeat()):
            doc = wnd.document
            tol, eol = doc.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)

            with wnd.document.undo_group():
                mode = wnd.document.mode
                while tol < wnd.screen.selection.get_selrange()[1]:
                    f, t = mode.get_indent_range(tol)
                    if f != t:
                        cols = mode.calc_cols(f, t)
                    else:
                        cols = 0

                    if cols:
                        s = mode.build_indent_str(
                            max(0, cols - mode.indent_width))
                        mode.replace_string(wnd, f, t, s, False)

                    tol = doc.geteol(tol)

        f, t = wnd.screen.selection.get_selrange()
        wnd.cursor.setpos(f)
        wnd.cursor.savecol()

    def _undo(self, wnd, rec):
        (action, args, kwargs) = rec
        if action == wnd.document.mode.UNDO_INSERT:
            pos, s, cur_pos, newpos = args
            wnd.document.delete(pos, pos + len(s))
            return cur_pos
        elif action == wnd.document.mode.UNDO_REPLACE:
            pos, posto, s, deled, cur_pos, newpos = args
            wnd.document.replace(pos, pos + len(s), deled)
            return cur_pos
        else:
            pos, posto, deled, cur_pos, newpos = args
            wnd.document.insert(pos, deled)

        return cur_pos

    @commandid('edit.undo')
    @norerun
    def undo(self, wnd):
        for i in range(wnd.get_command_repeat()):
            if wnd.document.undo and wnd.document.undo.can_undo():
                wnd.screen.selection.clear()
                pos = None
                for rec in wnd.document.undo.undo():
                    pos = self._undo(wnd, rec)

                if pos is not None:
                    wnd.cursor.setpos(pos)
                    wnd.cursor.savecol()

                wnd.document.mode.on_edited(wnd)

    def _redo(self, wnd, rec):
        (action, args, kwargs) = rec
        if action == wnd.document.mode.UNDO_INSERT:
            pos, s, cur_pos, newpos = args
            wnd.document.insert(pos, s)
            return newpos
        elif action == wnd.document.mode.UNDO_REPLACE:
            pos, posto, s, deled, cur_pos, newpos = args
            wnd.document.replace(pos, posto, s)
            return pos
        else:
            pos, posto, deled, cur_pos, newpos = args
            wnd.document.delete(pos, posto)

        return newpos

    @commandid('edit.redo')
    @norerun
    def redo(self, wnd):
        for i in range(wnd.get_command_repeat()):
            if wnd.document.undo and wnd.document.undo.can_redo():
                wnd.screen.selection.clear()
                pos = None
                for rec in wnd.document.undo.redo():
                    pos = self._redo(wnd, rec)

                if pos is not None:
                    wnd.cursor.setpos(pos)
                    wnd.cursor.savecol()

                wnd.document.mode.on_edited(wnd)

    def _get_sel(self, wnd):
        if wnd.screen.selection.is_selected():
            if not wnd.screen.selection.is_rectangular():
                f, t = wnd.screen.selection.get_selrange()
                return wnd.document.gettext(f, t)
            else:
                s = []
                (posfrom, posto, colfrom, colto
                 ) = wnd.screen.selection.get_rect_range()

                while posfrom < posto:
                    sel = wnd.screen.selection.get_col_string(
                        posfrom, colfrom, colto)
                    if sel:
                        f, t, org = sel
                        s.append(org.rstrip('\n'))
                    else:
                        s.append('')
                    posfrom = wnd.document.geteol(posfrom)

                return '\n'.join(s)

    def _copy_sel(self, wnd):
        sel = self._get_sel(wnd)
        if sel:
            kaa.app.clipboard.set(sel)
        return sel

    @commandid('edit.copy')
    def copy(self, wnd):
        self._copy_sel(wnd)
        wnd.screen.selection.set_mark(None)

    @commandid('edit.cut')
    def cut(self, wnd):
        if self._copy_sel(wnd):
            self.delete_sel(wnd)
        wnd.screen.selection.clear()

    @commandid('edit.paste')
    def paste(self, wnd):
        s = kaa.app.clipboard.get()
        if s:
            with wnd.document.undo_group():
                for i in range(wnd.get_command_repeat()):
                    wnd.document.mode.put_string(wnd, s)
                    wnd.screen.selection.clear()

    @commandid('edit.conv.upper')
    def conv_upper(self, wnd):
        s = self._get_sel(wnd)
        if s:
            wnd.document.mode.put_string(wnd, s.upper())
            wnd.screen.selection.clear()

    @commandid('edit.conv.lower')
    def conv_lower(self, wnd):
        s = self._get_sel(wnd)
        if s:
            wnd.document.mode.put_string(wnd, s.lower())
            wnd.screen.selection.clear()

    @commandid('edit.conv.nfkc')
    def conv_nfkc(self, wnd):
        s = self._get_sel(wnd)
        if s:
            wnd.document.mode.put_string(wnd, unicodedata.normalize('NFKC', s))
            wnd.screen.selection.clear()

    @commandid('edit.conv.full-width')
    def conv_fullwidth(self, wnd):
        import pyjf3
        s = self._get_sel(wnd)
        if s:
            wnd.document.mode.put_string(wnd, pyjf3.tofull(s))
            wnd.screen.selection.clear()

    @commandid('edit.word-complete')
    @norec
    @norerun
    def complete(self, wnd):
        from kaa.ui.wordcomplete import wordcompletemode
        wordcompletemode.show_wordlist(wnd)

    @commandid('edit.clipboard-history')
    @norec
    @norerun
    def clipboard_history(self, wnd):
        words = list(kaa.app.clipboard.get_all())
        if not words:
            return

        def callback(text):
            if text:
                wnd.document.mode.put_string(wnd, text)
                wnd.screen.selection.clear()
                kaa.app.clipboard.set(text)

        from kaa.ui.texthist import texthistmode
        texthistmode.show_history('Search clipboard text:', callback, words)


class CodeCommands(Commands):

    @commandid('code.region.linecomment')
    def linecomment(self, wnd):
        if not wnd.screen.selection.is_selected():
            tol = wnd.document.gettol(wnd.cursor.pos)
            wnd.document.mode.insert_string(
                wnd, tol, wnd.document.mode.LINE_COMMENT,
                update_cursor=False)
            wnd.cursor.setpos(tol)
            wnd.cursor.savecol()
            return
        else:
            tol, eol = wnd.document.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)

            with wnd.document.undo_group():
                while tol < wnd.screen.selection.get_selrange()[1]:
                    wnd.document.mode.insert_string(
                        wnd, tol, wnd.document.mode.LINE_COMMENT,
                        update_cursor=False)
                    tol = wnd.document.geteol(tol)

            f, t = wnd.screen.selection.get_selrange()
            wnd.cursor.setpos(f)
            wnd.cursor.savecol()

    def _is_comment_line(self, wnd, pos):
        reobj = doc_re.compile(r'[ \t]*({})'.format(
            doc_re.escape(wnd.document.mode.LINE_COMMENT)))
        return reobj.match(wnd.document, pos)

    @commandid('code.region.unlinecomment')
    def uncomment(self, wnd):
        if not wnd.screen.selection.is_selected():
            tol = wnd.document.gettol(wnd.cursor.pos)
            m = self._is_comment_line(wnd, tol)
            if m:
                f, t = m.span(1)
                wnd.document.mode.delete_string(
                    wnd, f, t)
            return
        else:
            tol, eol = wnd.document.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)

            with wnd.document.undo_group():
                while tol < wnd.screen.selection.get_selrange()[1]:
                    m = self._is_comment_line(wnd, tol)
                    if m:
                        f, t = m.span(1)
                        wnd.document.mode.delete_string(
                            wnd, f, t, update_cursor=False)
                    tol = wnd.document.geteol(tol)

            f, t = wnd.screen.selection.get_selrange()
            wnd.cursor.setpos(f)
            wnd.cursor.savecol()


class SearchCommands(Commands):

    @commandid('search.showsearch')
    @norec
    @norerun
    def showsearch(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        doc = document.Document()
        mode = searchdlgmode.SearchDlgMode(target=wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_inputline(doc)

    @commandid('search.showreplace')
    @norec
    @norerun
    def showreplace(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        doc = document.Document()
        mode = searchdlgmode.ReplaceDlgMode(target=wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_inputline(doc)

    def _show_searchresult(self, wnd, hit):
        if hit:
            f, t = hit.span()
            wnd.cursor.setpos(f)
            wnd.screen.selection.set_range(f, t)
            kaa.app.messagebar.set_message('found')
        else:
            kaa.app.messagebar.set_message('not found')

    @commandid('search.next')
    @norerun
    def searchnext(self, wnd):
        if not modebase.SearchOption.LAST_SEARCH:
            return
        if not modebase.SearchOption.LAST_SEARCH.text:
            return
        range = wnd.screen.selection.get_selrange()
        if range:
            start = range[0] + 1
        else:
            start = wnd.cursor.pos

        ret = wnd.document.mode.search_next(
            start, modebase.SearchOption.LAST_SEARCH)
        self._show_searchresult(wnd, ret)

        if not ret:
            if start != 0:
                ret = wnd.document.mode.search_next(
                    0, modebase.SearchOption.LAST_SEARCH)
                self._show_searchresult(wnd, ret)

    @commandid('search.prev')
    @norerun
    def searchprev(self, wnd):
        if not modebase.SearchOption.LAST_SEARCH:
            return
        if not modebase.SearchOption.LAST_SEARCH.text:
            return
        range = wnd.screen.selection.get_selrange()
        if range:
            start = range[1] - 1
        else:
            start = wnd.cursor.pos

        ret = wnd.document.mode.search_prev(
            start, modebase.SearchOption.LAST_SEARCH)
        self._show_searchresult(wnd, ret)

        if not ret:
            if start != wnd.document.endpos():
                ret = wnd.document.mode.search_prev(
                    wnd.document.endpos(),
                    modebase.SearchOption.LAST_SEARCH)
                self._show_searchresult(wnd, ret)
