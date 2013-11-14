import itertools
import re
import unicodedata
import kaa
from kaa.command import Commands, command, is_enable, norec, norerun
from kaa import document
from kaa.filetype.default import modebase
from gappedbuf import re as gre


class CursorCommands(Commands):
    
    @command('cursor.right')
    @norerun
    def right(self, wnd):
        if wnd.screen.selection.has_mark():
            wnd.cursor.right()
        elif wnd.screen.selection.is_selected():
            range = wnd.screen.selection.get_selrange()
            if wnd.cursor.pos >= range[1]:
                wnd.cursor.right()
            else:
                wnd.cursor.setpos(wnd.cursor.adjust_nextpos(
                                    wnd.cursor.pos, range[1]))
        else:
            wnd.cursor.right()
            
        wnd.screen.selection.end_cursor()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.right.select')
    @norerun
    def right_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.right()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.left')
    @norerun
    def left(self, wnd):
        if wnd.screen.selection.has_mark():
            wnd.cursor.left()
        elif wnd.screen.selection.is_selected():
            range = wnd.screen.selection.get_selrange()
            if wnd.cursor.pos <= range[0]:
                wnd.cursor.left()
            else:
                wnd.cursor.setpos(wnd.cursor.adjust_nextpos(
                                    wnd.cursor.pos, range[0]))
        else:
            wnd.cursor.left()
            
        wnd.screen.selection.end_cursor()
        wnd.screen.selection.set_to(wnd.cursor.pos)


    @command('cursor.left.select')
    @norerun
    def left_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.left()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.up')
    @norerun
    def up(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.up()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.up.select')
    @norerun
    def up_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.up()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.down')
    @norerun
    def down(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.down()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.down.select')
    @norerun
    def down_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.down()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.prev-line')
    @norerun
    def prev_line(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.prev_line()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.next-line')
    @norerun
    def next_line(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.next_line()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.word-right')
    @norerun
    def word_right(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.right(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.word-right.select')
    @norerun
    def word_right_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.right(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.word-left')
    @norerun
    def word_left(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.left(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.word-left.select')
    @norerun
    def word_left_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.left(word=True)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.pagedown')
    @norerun
    def pagedown(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.pagedown()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.pagedown.select')
    @norerun
    def pagedown_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.pagedown()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.pageup')
    @norerun
    def pageup(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.pageup()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.pageup.select')
    @norerun
    def pageup_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.pageup()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.home')
    @norerun
    def home(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.home()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.home.select')
    @norerun
    def home_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.home()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.end')
    @norerun
    def end(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.end()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.end.select')
    @norerun
    def end_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.end()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.top-of-line')
    @norerun
    def tol(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.tol(wnd.cursor.pos)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.end-of-line')
    @norerun
    def eol(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.eol(wnd.cursor.pos)
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.top-of-file')
    @norerun
    def top(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.tof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.top-of-file.select')
    @norerun
    def top_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.tof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.end-of-file')
    @norerun
    def last(self, wnd):
        wnd.screen.selection.end_cursor()
        wnd.cursor.eof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.end-of-file.select')
    @norerun
    def last_select(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)
        wnd.cursor.eof()
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('cursor.go-to-line')
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

            wnd.screen.selection.end_cursor()
            
            pos = wnd.document.get_lineno_pos(lineno)
            tol = wnd.document.gettol(pos)
            wnd.cursor.setpos(wnd.cursor.adjust_nextpos(wnd.cursor.pos, tol))

            popup = w.get_label('popup')
            popup.destroy()

        def filter(wnd, s):
            if s == '0':
                t = wnd.document.mode.get_input_text().strip()
                if not t or int(t) == 0:
                    return ''
            return re.match(r'\d*', s).group()

        from kaa.ui.inputline import inputlinemode
        doc = inputlinemode.InputlineMode.build('Line number:', callback, filter=filter)
        kaa.app.messagebar.set_message("Enter line number")

        kaa.app.show_dialog(doc)


class ScreenCommands(Commands):
    @command('selection.begin-cursor')
    @norerun
    def selection_begin(self, wnd):
        wnd.screen.selection.begin_cursor(wnd.cursor.pos)

    @command('selection.set-to')
    @norerun
    def selection_set_end(self, wnd):
        wnd.screen.selection.set_to(wnd.cursor.pos)

    @command('selection.end-cursor')
    @norerun
    def selection_clear(self, wnd):
        wnd.screen.selection.end_cursor()

    @command('selection.set-mark')
    @norerun
    def selection_set_mark(self, wnd):
        if not wnd.screen.selection.has_mark():
            wnd.screen.selection.set_mark(wnd.cursor.pos)
        else:
            wnd.screen.selection.set_mark(None)

    @command('selection.set-rectangle-mark')
    @norerun
    def selection_set_rectangle_mark(self, wnd):
        if not wnd.screen.selection.has_mark():
            wnd.screen.selection.set_rectangle_mark(wnd.cursor.pos)
        else:
            wnd.screen.selection.set_rectangle_mark(None)

    @command('selection.all')
    @norerun
    def select_all(self, wnd):
        f = wnd.cursor.adjust_nextpos(wnd.cursor.pos, 0)
        t = wnd.cursor.adjust_nextpos(wnd.cursor.pos, wnd.document.endpos())
        wnd.screen.selection.set_range(f, t)

    @command('selection.curline')
    @norerun
    def select_cur_line(self, wnd):
        tol = wnd.cursor.adjust_nextpos(
                wnd.cursor.pos,
                wnd.document.gettol(wnd.cursor.pos))
        eol = wnd.cursor.adjust_nextpos(
                wnd.cursor.pos,
                wnd.document.geteol(tol))

        wnd.screen.selection.set_range(tol, eol)

    @command('selection.curword')
    @norerun
    def select_cur_word(self, wnd):
        ret = wnd.document.mode.get_word_at(wnd.cursor.pos)
        if ret:
            f, t, cg = ret
            f = wnd.cursor.adjust_nextpos(wnd.cursor.pos, f)
            t = wnd.cursor.adjust_nextpos(wnd.cursor.pos, t)

            wnd.screen.selection.set_range(f, t)

    @command('selection.expand-sel')
    @norerun
    @norec
    def expand_sel(self, wnd):
        mode = wnd.document.mode
        keys = wnd.editmode.last_command_keys
        L = len(keys)

        if L >= 3 and keys[-1] == keys[-2] == keys[-3]:
            self.select_all(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(self.select_all)

        elif L >= 2 and (keys[-1] == keys[-2]):
            self.select_cur_line(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(self.select_cur_line)

        else:
            self.select_cur_word(wnd)
            if kaa.app.macro.recording:
                kaa.app.macro.record(self.select_cur_word)

    @command('screen.lineselection.begin')
    @norerun
    def lineselection_begin(self, wnd):
        tol = wnd.cursor.adjust_nextpos(wnd.document.gettol(wnd.cursor.pos))
        wnd.screen.selection.begin_cursor(tol)

    @command('screen.lineselection.set-end')
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
    (UNDO_INSERT,
     UNDO_REPLACE,
     UNDO_DELETE) = range(3)

    def on_edited(self, wnd):
        wnd.document.mode.on_edited(wnd)

    def insert_string(self, wnd, pos, s, update_cursor=True):
        """Insert string"""

        cur_pos = wnd.cursor.pos

        wnd.document.insert(pos, s)

        if update_cursor:
            wnd.cursor.setpos(wnd.cursor.pos+len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_INSERT, pos, s,
                                  cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def replace_string(self, wnd, pos, posto, s, update_cursor=True):
        """Replace string"""

        cur_pos = wnd.cursor.pos

        deled = wnd.document.gettext(pos, posto)
        wnd.document.replace(pos, posto, s)

        if update_cursor:
            wnd.cursor.setpos(pos+len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_REPLACE, pos, posto, s,
                                  deled, cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def delete_string(self, wnd, pos, posto, update_cursor=True):
        """Delete string"""

        cur_pos = wnd.cursor.pos

        if pos < posto:
            deled = wnd.document.gettext(pos, posto)
            wnd.document.delete(pos, posto)

            if update_cursor:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            if wnd.document.undo:
                wnd.document.undo.add(self.UNDO_DELETE, pos, posto, deled,
                                      cur_pos, wnd.cursor.pos)
            self.on_edited(wnd)

    def replace_rect(self, wnd, repto):
        if wnd.document.undo:
            wnd.document.undo.beginblock()
        try:
            (posfrom, posto, colfrom, colto
                ) = wnd.screen.selection.get_rect_range()

            for s in repto:
                if posto <= posfrom:
                    break
                    
                sel = wnd.screen.selection.get_col_string(
                        posfrom, colfrom, colto)
                if sel:
                    f, t, org = sel
                    if org.endswith('\n'):
                        t = max(f, t-1)
                    self.replace_string(wnd, f, t, s)
                    posto += (len(s) - (t-f))
                posfrom = wnd.document.geteol(posfrom)
        finally:
            if wnd.document.undo:
                wnd.document.undo.endblock()
            
    def put_string(self, wnd, s):
        s = wnd.document.mode.filter_string(wnd, s)

        if wnd.screen.selection.is_selected():
            if wnd.screen.selection.is_rectangular():
                if '\n' not in s:
                    self.replace_rect(wnd, itertools.repeat(s))
                else:
                    self.replace_rect(wnd, s.split('\n'))
                    
            else:
                sel = wnd.screen.selection.get_selrange()
                f, t = sel
                self.replace_string(wnd, f, t, s)
        else:
            self.insert_string(wnd, wnd.cursor.pos, s)

    def delete_sel(self, wnd):
        if wnd.screen.selection.is_selected():
            if not wnd.screen.selection.is_rectangular():
                sel = wnd.screen.selection.get_selrange()
                wnd.screen.selection.clear()
                if sel:
                    f, t = sel
                    self.delete_string(wnd, f, t)
                    return True
            else:
                return self._delete_rect_sel(wnd)

    def _delete_rect_sel(self, wnd):
        if wnd.document.undo:
            wnd.document.undo.beginblock()
        try:
            (posfrom, posto, colfrom, colto
                ) = wnd.screen.selection.get_rect_range()

            while posfrom < posto:
                sel = wnd.screen.selection.get_col_string(
                        posfrom, colfrom, colto)
                if sel:
                    f, t, org = sel
                    if org.endswith('\n'):
                        t = max(f, t-1)
                    self.delete_string(wnd, f, t)
                    posto -= (t-f)
                posfrom = wnd.document.geteol(posfrom)
                
            return True
        finally:
            if wnd.document.undo:
                wnd.document.undo.endblock()

    @command('edit.delete')
    def delete(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        nextpos = wnd.document.get_nextpos(pos)
        nextpos = wnd.cursor.adjust_nextpos(pos, nextpos)
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.delete.word')
    def delete_word(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        wnd.cursor.right(word=True)
        nextpos = wnd.cursor.pos
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.delete.line')
    def delete_line(self, wnd):
        pos = wnd.cursor.pos
        nextpos = wnd.cursor.adjust_nextpos(pos, wnd.document.find_newline(pos))
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.delete.currentline')
    def delete_currentline(self, wnd):
        pos = wnd.cursor.pos
        f = wnd.cursor.adjust_nextpos(pos, wnd.document.gettol(pos))
        t = wnd.cursor.adjust_nextpos(pos, wnd.document.geteol(f))

        if f < t:
            self.delete_string(wnd, f, t)

    @command('edit.backspace')
    def backspace(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        prevpos = wnd.cursor.adjust_nextpos(
            pos, wnd.document.get_prevpos(pos))
        if prevpos < pos:
            if pos == wnd.screen.pos:
                # locate cursor before delete to scroll half page up
                wnd.cursor.setpos(prevpos)

            self.delete_string(wnd, prevpos, pos)

    @command('edit.backspace.word')
    def backspace_word(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        wnd.cursor.left(word=True)
        prevpos = wnd.cursor.pos
        if prevpos < pos:
            if prevpos < wnd.screen.pos:
                # locate cursor before delete to scroll half page up
                wnd.cursor.setpos(prevpos)

            self.delete_string(wnd, prevpos, pos)

    @command('edit.newline')
    @norerun
    def newline(self, wnd):
        if not wnd.document.mode.auto_indent:
            self.put_string(wnd, '\n')
            wnd.screen.selection.clear()
            return

        wnd.screen.selection.clear()
        indent = wnd.document.mode.on_auto_indent(wnd)

    def _indent_line(self, wnd, pos):
        mode = wnd.document.mode
        f, t = mode.get_indent_range(pos)
        if pos > t:
            self.put_string(wnd, '\t')
            wnd.screen.selection.clear()
            return

        if f != t:
            cols = mode.calc_cols(f, t)
        else:
            cols = 0

        s = mode.build_indent_str(cols+mode.indent_width)
        self.replace_string(wnd, f, t, s, True)

    @command('edit.indent')
    def indent(self, wnd):
        if not wnd.screen.selection.is_selected():
            self._indent_line(wnd, wnd.cursor.pos)
            return

        doc = wnd.document
        tol, eol = doc.mode.get_line_sel(wnd)
        wnd.screen.selection.set_range(tol, eol)

        if wnd.document.undo:
            wnd.document.undo.beginblock()
        try:
            mode = wnd.document.mode
            while tol < wnd.screen.selection.get_end():
                f, t = mode.get_indent_range(tol)
                if f != t:
                    cols = mode.calc_cols(f, t)
                else:
                    cols = 0

                s = mode.build_indent_str(cols+mode.indent_width)
                self.replace_string(wnd, f, t, s, False)
                tol = doc.geteol(tol)
        finally:
            if wnd.document.undo:
                wnd.document.undo.endblock()
                
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

        s = mode.build_indent_str(max(0, cols-mode.indent_width))
        self.replace_string(wnd, f, t, s, True)

    @command('edit.dedent')
    def dedent(self, wnd):
        if not wnd.screen.selection.is_selected():
            self._dedent_line(wnd, wnd.cursor.pos)
            return

        doc = wnd.document
        tol, eol = doc.mode.get_line_sel(wnd)
        wnd.screen.selection.set_range(tol, eol)

        if wnd.document.undo:
            wnd.document.undo.beginblock()
        try:
            mode = wnd.document.mode
            while tol < wnd.screen.selection.get_end():
                f, t = mode.get_indent_range(tol)
                if f != t:
                    cols = mode.calc_cols(f, t)
                else:
                    cols = 0

                if cols:
                    s = mode.build_indent_str(max(0, cols-mode.indent_width))
                    self.replace_string(wnd, f, t, s, False)

                tol = doc.geteol(tol)
        finally:
            if wnd.document.undo:
                wnd.document.undo.endblock()
                
        f, t = wnd.screen.selection.get_selrange()
        wnd.cursor.setpos(f)
        wnd.cursor.savecol()

    def _undo(self, wnd, rec):
        (action, args, kwargs) = rec
        if action == self.UNDO_INSERT:
            pos, s, cur_pos, newpos = args
            wnd.document.delete(pos, pos+len(s))
            return cur_pos
        elif action == self.UNDO_REPLACE:
            pos, posto, s, deled, cur_pos, newpos = args
            wnd.document.replace(pos, pos+len(s), deled)
            return cur_pos
        else:
            pos, posto, deled, cur_pos, newpos = args
            wnd.document.insert(pos, deled)

        return cur_pos

    @command('edit.undo')
    @norerun
    def undo(self, wnd):
        if wnd.document.undo and wnd.document.undo.can_undo():
            wnd.screen.selection.clear()
            pos = None
            for rec in wnd.document.undo.undo():
                pos = self._undo(wnd, rec)

            if pos is not None:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            self.on_edited(wnd)

    def _redo(self, wnd, rec):
        (action, args, kwargs) = rec
        if action == self.UNDO_INSERT:
            pos, s, cur_pos, newpos = args
            wnd.document.insert(pos, s)
            return newpos
        elif action == self.UNDO_REPLACE:
            pos, posto, s, deled, cur_pos, newpos = args
            wnd.document.replace(pos, posto, s)
            return pos
        else:
            pos, posto, deled, cur_pos, newpos = args
            wnd.document.delete(pos, posto)

        return newpos

    @command('edit.redo')
    @norerun
    def redo(self, wnd):
        if wnd.document.undo and wnd.document.undo.can_redo():
            wnd.screen.selection.clear()
            pos = None
            for rec in wnd.document.undo.redo():
                pos = self._redo(wnd, rec)

            if pos is not None:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            self.on_edited(wnd)

    def _get_sel(self, wnd):
        if wnd.screen.selection.is_selected():
            if not wnd.screen.selection.is_rectangular():
                f, t =wnd.screen.selection.get_selrange()
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
            kaa.app.set_clipboard(sel)
        return sel
        
    @command('edit.copy')
    def copy(self, wnd):
        self._copy_sel(wnd)
        wnd.screen.selection.set_mark(None)

    @command('edit.cut')
    def cut(self, wnd):
        if self._copy_sel(wnd):
            self.delete_sel(wnd)
        wnd.screen.selection.clear()

    @command('edit.paste')
    def paste(self, wnd):
        s = kaa.app.get_clipboard()
        if s:
            self.put_string(wnd, s)
            wnd.screen.selection.clear()

    @command('edit.conv.upper')
    def conv_upper(self, wnd):
        s = self._get_sel(wnd)
        if s:
            self.put_string(wnd, s.upper())
            wnd.screen.selection.clear()

    @command('edit.conv.lower')
    def conv_lower(self, wnd):
        s = self._get_sel(wnd)
        if s:
            self.put_string(wnd, s.lower())
            wnd.screen.selection.clear()

    @command('edit.conv.nfkc')
    def conv_nfkc(self, wnd):
        s = self._get_sel(wnd)
        if s:
            self.put_string(wnd, unicodedata.normalize('NFKC', s))
            wnd.screen.selection.clear()

    @command('edit.conv.full-width')
    def conv_fullwidth(self, wnd):
        import pyjf3
        s = self._get_sel(wnd)
        if s:
            self.put_string(wnd, pyjf3.tofull(s))
            wnd.screen.selection.clear()

    @command('edit.word-complete')
    @norec
    @norerun
    def complete(self, wnd):
        from kaa.ui.wordcomplete import wordcompletemode
        wordcompletemode.show_wordlist(wnd)

    @command('edit.clipboard-history')
    @norec
    @norerun
    def clipboard_history(self, wnd):
        from kaa.ui.clipboardhist import clipboardhistmode
        clipboardhistmode.show_history(wnd)

class CodeCommands(Commands):
    @command('code.region.linecomment')
    def linecomment(self, wnd):
        if not wnd.screen.selection.is_selected():
            tol = wnd.document.gettol(wnd.cursor.pos)
            wnd.document.mode.edit_commands.insert_string(
                    wnd, tol, wnd.document.mode.LINE_COMMENT, 
                    update_cursor=False)
            wnd.cursor.setpos(tol)
            wnd.cursor.savecol()
            return
        else:
            tol, eol = wnd.document.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)
    
            if wnd.document.undo:
                wnd.document.undo.beginblock()
            try:
                mode = wnd.document.mode
                while tol < wnd.screen.selection.get_end():
                    wnd.document.mode.edit_commands.insert_string(
                        wnd, tol, wnd.document.mode.LINE_COMMENT, 
                        update_cursor=False)
                    tol = wnd.document.geteol(tol)
            finally:
                if wnd.document.undo:
                    wnd.document.undo.endblock()

            f, t = wnd.screen.selection.get_selrange()
            wnd.cursor.setpos(f)
            wnd.cursor.savecol()

    def _is_comment_line(self, wnd, pos):
        reobj = gre.compile(r'[ \t]*({})'.format(
                    gre.escape(wnd.document.mode.LINE_COMMENT)))
        return reobj.match(wnd.document.buf, pos)
        
    @command('code.region.unlinecomment')
    def uncomment(self, wnd):
        if not wnd.screen.selection.is_selected():
            tol = wnd.document.gettol(wnd.cursor.pos)
            m = self._is_comment_line(wnd, tol)
            if m:
                f, t = m.span(1)
                wnd.document.mode.edit_commands.delete_string(
                    wnd, f, t)
            return
        else:
            tol, eol = wnd.document.mode.get_line_sel(wnd)
            wnd.screen.selection.set_range(tol, eol)
    
            if wnd.document.undo:
                wnd.document.undo.beginblock()
            try:
                mode = wnd.document.mode
                while tol < wnd.screen.selection.get_end():
                    m = self._is_comment_line(wnd, tol)
                    if m:
                        f, t = m.span(1)
                        wnd.document.mode.edit_commands.delete_string(
                            wnd, f, t, update_cursor=False)
                    tol = wnd.document.geteol(tol)
            finally:
                if wnd.document.undo:
                    wnd.document.undo.endblock()

            f, t = wnd.screen.selection.get_selrange()
            wnd.cursor.setpos(f)
            wnd.cursor.savecol()

class MacroCommands(Commands):
    @command('macro.start-record')
    @norec
    @norerun
    def start_record(self, wnd):
        kaa.app.macro.start_record()
        kaa.app.messagebar.update()

    @command('macro.end-record')
    @norec
    @norerun
    def end_record(self, wnd):
        kaa.app.macro.end_record()
        kaa.app.messagebar.update()

    @command('macro.toggle-record')
    @norec
    @norerun
    def toggle_record(self, wnd):
        kaa.app.macro.toggle_record()
        kaa.app.messagebar.update()

    @command('macro.run')
    @norec
    def run_macro(self, wnd):
        if kaa.app.macro.is_recording():
            return
        if not kaa.app.macro.get_commands():
            return

        if wnd.document.undo:
            wnd.document.undo.beginblock()
        try:
            kaa.app.macro.run(wnd)
        finally:
            if wnd.document.undo:
                wnd.document.undo.endblock()


class SearchCommands(Commands):
    @command('search.showsearch')
    @norec
    @norerun
    def showsearch(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        mode = searchdlgmode.SearchDlgMode(target=wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_inputline(doc)

    @command('search.showreplace')
    @norec
    @norerun
    def showreplace(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
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

    @command('search.next')
    @norerun
    def searchnext(self, wnd):
        if not modebase.SearchOption.LAST_SEARCH:
            return
        if not modebase.SearchOption.LAST_SEARCH.text:
            return
        range = wnd.screen.selection.get_selrange()
        if range:
            start = range[0]+1
        else:
            start =  wnd.cursor.pos

        ret = wnd.document.mode.search_next(start, modebase.SearchOption.LAST_SEARCH)
        self._show_searchresult(wnd, ret)

        if not ret:
            if start != 0:
                ret = wnd.document.mode.search_next(0, modebase.SearchOption.LAST_SEARCH)
                self._show_searchresult(wnd, ret)

    @command('search.prev')
    @norerun
    def searchprev(self, wnd):
        if not modebase.SearchOption.LAST_SEARCH:
            return
        if not modebase.SearchOption.LAST_SEARCH.text:
            return
        range = wnd.screen.selection.get_selrange()
        if range:
            start = range[1]-1
        else:
            start =  wnd.cursor.pos

        ret = wnd.document.mode.search_prev(start, modebase.SearchOption.LAST_SEARCH)
        self._show_searchresult(wnd, ret)

        if not ret:
            if start != wnd.document.endpos():
                ret = wnd.document.mode.search_prev(wnd.document.endpos(),
                                                    modebase.SearchOption.LAST_SEARCH)
                self._show_searchresult(wnd, ret)

    @command('search.showgrep')
    @norec
    @norerun
    def showgrep(self, wnd):
        from kaa.ui.grep import grepdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        mode = grepdlgmode.GrepDlgMode(wnd)
        doc.setmode(mode)
        mode.build_document()

        kaa.app.show_dialog(doc)


