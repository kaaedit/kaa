
import kaa_testutils
from kaa.commands import editorcommand


class TestCursor(kaa_testutils._TestScreenBase):

    def test_cursor(self):
        wnd = self._getwnd("abc\ndef\n")

        cmd = editorcommand.CursorCommands()
        cmd.right(wnd)
        assert wnd.cursor.pos == 1

        cmd.left(wnd)
        assert wnd.cursor.pos == 0

        cmd.down(wnd)
        assert wnd.cursor.pos == 4

        cmd.up(wnd)
        assert wnd.cursor.pos == 0


class TestEdit(kaa_testutils._TestScreenBase):

    def test_putstring(self):
        wnd = self._getwnd("abc\ndef\n")

        wnd.document.mode.put_string(wnd, '12345')
        assert wnd.document.gettext(0, 5) == '12345'

    def test_delete(self):
        wnd = self._getwnd("abc\ndef\n")

        cmd = editorcommand.EditCommands()
        cmd.delete(wnd)
        assert wnd.document.gettext(0, 2) == 'bc'

        wnd = self._getwnd("a\u0301bc\ndef\n")

        cmd = editorcommand.EditCommands()
        cmd.delete(wnd)
        assert wnd.document.gettext(0, 2) == 'bc'

    def test_backspace(self):
        wnd = self._getwnd("abc\ndef\n")

        wnd.cursor.setpos(1)
        cmd = editorcommand.EditCommands()
        cmd.backspace(wnd)
        assert wnd.document.gettext(0, 2) == 'bc'
        assert wnd.cursor.pos == 0

        wnd = self._getwnd("a\u0302bc\ndef\n")

        wnd.cursor.setpos(2)
        cmd = editorcommand.EditCommands()
        cmd.backspace(wnd)
        assert wnd.document.gettext(0, 2) == 'bc'
        assert wnd.cursor.pos == 0

    def test_lineindent(self):
        wnd = self._getwnd("abc")
        wnd.cursor.setpos(0)
        cmd = editorcommand.EditCommands()
        cmd.indent(wnd)
        assert wnd.document.gettext(0, 7) == '    abc'

    def test_blockindent(self):
        wnd = self._getwnd("abc\ndef\nghi")
        wnd.screen.selection.set_range(1, 9)
        cmd = editorcommand.EditCommands()
        cmd.indent(wnd)
        assert wnd.document.gettext(0, 7) == '    abc'

    def test_blockindentblanklines(self):
        wnd = self._getwnd("abc\n\ndef method")
        wnd.screen.selection.set_range(1, 6)
        cmd = editorcommand.EditCommands()
        cmd.indent(wnd)
        assert wnd.document.gettext(0, 16) == "    abc\n\n    def"

        wnd = self._getwnd("a\na")
        wnd.screen.selection.set_range(0, 3)
        cmd.indent(wnd)
        assert wnd.document.gettext(0, 12) == "    a\n    a"

    def test_undo_ins(self):
        wnd = self._getwnd("")
        cmd = editorcommand.EditCommands()

        wnd.document.mode.put_string(wnd, 'abc')

        cmd.undo(wnd)
        assert wnd.document.endpos() == 0

        cmd.redo(wnd)
        assert wnd.document.gettext(0, 3) == 'abc'

    def test_undo_delete(self):
        wnd = self._getwnd("abc")
        cmd = editorcommand.EditCommands()

        cmd.delete(wnd)

        cmd.undo(wnd)
        assert wnd.document.gettext(0, 3) == 'abc'

        cmd.redo(wnd)
        assert wnd.document.gettext(0, 2) == 'bc'

    def test_undo_backspace(self):
        wnd = self._getwnd("abc")
        cmd = editorcommand.EditCommands()

        wnd.cursor.setpos(1)
        cmd.backspace(wnd)

        cmd.undo(wnd)
        assert wnd.document.gettext(0, 3) == 'abc'
        assert wnd.cursor.pos == 1

        cmd.redo(wnd)
        assert wnd.document.gettext(0, 2) == 'bc'
        assert wnd.cursor.pos == 0

    def test_undo_newline(self):
        wnd = self._getwnd("    abc")
        cmd = editorcommand.EditCommands()

        wnd.cursor.setpos(7)
        cmd.newline(wnd)

        assert wnd.document.gettext(0, 7) == '    abc'
        assert wnd.document.gettext(7, 12) == '\n    '

        wnd = self._getwnd("      abc")
        cmd = editorcommand.EditCommands()

        wnd.cursor.setpos(4)
        cmd.newline(wnd)

        assert wnd.document.gettext(0, 5) == '\n    '
        assert wnd.document.gettext(5, 15) == '  abc'
