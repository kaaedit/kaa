import kaa
from kaa.command import Commands, command, is_enable, norec, repeat
from kaa import LOG
from kaa import document



class CursorCommands(Commands):
    @command('cursor.right')
    @repeat
    def right(self, wnd):
        wnd.cursor.right()

    @command('cursor.left')
    @repeat
    def left(self, wnd):
        wnd.cursor.left()

    @command('cursor.up')
    @repeat
    def up(self, wnd):
        wnd.cursor.up()

    @command('cursor.down')
    @repeat
    def down(self, wnd):
        wnd.cursor.down()

    @command('cursor.word-right')
    @repeat
    def word_right(self, wnd):
        wnd.cursor.right(word=True)

    @command('cursor.word-left')
    @repeat
    def word_left(self, wnd):
        wnd.cursor.left(word=True)

    @command('cursor.pagedown')
    @repeat
    def pagedown(self, wnd):
        wnd.cursor.pagedown()

    @command('cursor.pageup')
    @repeat
    def pageup(self, wnd):
        wnd.cursor.pageup()


class ScreenCommands(Commands):
    @command('screen.selection.begin')
    def selection_begin(self, wnd):
        wnd.screen.selection.start_selection(wnd.cursor.pos)

    @command('screen.selection.set_end')
    def selection_set_end(self, wnd):
        wnd.screen.selection.set_end(wnd.cursor.pos)

    @command('screen.selection.clear')
    def selection_clear(self, wnd):
        wnd.screen.selection.clear()

    @command('screen.lineselection.curline')
    def select_cur_line(self, wnd):
        tol = wnd.document.gettol(wnd.cursor.pos)
        eol = wnd.document.geteol(tol)

        wnd.screen.selection.set_range(tol, eol)

    @command('screen.lineselection.begin')
    def lineselection_begin(self, wnd):
        tol = wnd.document.gettol(wnd.cursor.pos)
        wnd.screen.selection.start_selection(tol)

    @command('screen.lineselection.set_end')
    def lineselection_set_end(self, wnd):
        f = wnd.screen.selection.start
        if f is None:
            self.select_cur_line(wnd)
        else:
            pos = wnd.cursor.pos
            if pos < f:
                tol = wnd.document.gettol(pos)
                wnd.screen.selection.set_end(tol)
            else:
                eol = wnd.document.geteol(pos)
                wnd.screen.selection.set_end(eol)


class EditCommands(Commands):
    (UNDO_INSERT,
     UNDO_REPLACE,
     UNDO_DELETE) = range(3)

    def on_edited(self, wnd):
        pass

    def insert_string(self, wnd, pos, s, update_cursor=True):
        """Insert string"""

        wnd.screen.selection.clear()
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

        wnd.screen.selection.clear()
        cur_pos = wnd.cursor.pos

        deled = wnd.document.gettext(pos, posto)
        wnd.document.replace(pos, posto, s)

        if update_cursor:
            wnd.cursor.setpos(wnd.cursor.pos+len(s))
            wnd.cursor.savecol()

        if wnd.document.undo:
            wnd.document.undo.add(self.UNDO_REPLACE, pos, posto, s,
                                  deled, cur_pos, wnd.cursor.pos)

        self.on_edited(wnd)

    def delete_string(self, wnd, pos, posto, update_cursor=True):
        """Delete string"""

        wnd.screen.selection.clear()
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

    @command('edit.put-string')
    def put_string(self, wnd, s):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            self.replace_string(wnd, f, t, s)
        else:
            self.insert_string(wnd, wnd.cursor.pos, s)

    def delete_sel(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            self.delete_string(wnd, f, t)
            return True

    @command('edit.delete')
    @repeat
    def delete(self, wnd):
        if self.delete_sel(wnd):
            return

        pos = wnd.cursor.pos
        nextpos = wnd.document.get_nextpos(pos)
        nextpos = wnd.cursor.adjust_nextpos(pos, nextpos)
        if pos < nextpos:
            self.delete_string(wnd, pos, nextpos)

    @command('edit.backspace')
    @repeat
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
    def undo(self, wnd):
        if wnd.document.undo.can_undo():
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
    def redo(self, wnd):
        if wnd.document.undo.can_redo():
            wnd.screen.selection.clear()
            pos = None
            for rec in wnd.document.undo.redo():
                pos = self._redo(wnd, rec)

            if pos is not None:
                wnd.cursor.setpos(pos)
                wnd.cursor.savecol()

            self.on_edited(wnd)

    @command('edit.copy')
    def copy(self, wnd):
        sel = wnd.screen.selection.get_range()
        if sel:
            f, t = sel
            kaa.app.clipboard = wnd.document.gettext(f, t)

    @command('edit.cut')
    def cut(self, wnd):
        self.copy(wnd)
        self.delete_sel(wnd)

    @command('edit.paste')
    @repeat
    def paste(self, wnd):
        if kaa.app.clipboard:
            self.put_string(wnd, kaa.app.clipboard)


class MacroCommands(Commands):
    @command('macro.start-record')
    @norec
    def start_record(self, wnd):
        kaa.app.macro.start_record()

    @command('macro.end-record')
    @norec
    def end_record(self, wnd):
        kaa.app.macro.end_record()

    @command('macro.toggle-record')
    @norec
    def toggle_record(self, wnd):
        kaa.app.macro.toggle_record()

    @command('macro.run')
    @norec
    @repeat
    def run_macro(self, wnd):
        wnd.document.undo.beginblock()
        try:
            kaa.app.macro.run(wnd)
        finally:
            wnd.document.undo.endblock()


class SearchCommands(Commands):
    @command('search.showsearch')
    @norec
    def showsearch(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        doc.setmode(searchdlgmode.SearchDlgMode(target=wnd))

        kaa.app.show_inputline(doc)

    @command('search.showreplace')
    @norec
    def showreplace(self, wnd):
        from kaa.ui.searchdlg import searchdlgmode

        buf = document.Buffer()
        doc = document.Document(buf)
        doc.setmode(searchdlgmode.ReplaceDlgMode(target=wnd))

        kaa.app.show_inputline(doc)

