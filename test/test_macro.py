import kaa_testutils
from kaa.commands import editorcommand
import kaa.macro
from kaa.command import command, norec

class TestMacro(kaa_testutils._TestScreenBase):
    def test_toggle_record(self):
        macro = kaa.macro.Macro()
        assert not macro.is_recording()

        macro.toggle_record()
        assert macro.is_recording()

        macro.toggle_record()
        assert not macro.is_recording()

    def test_record(self):

        macro = kaa.macro.Macro()
        macro.toggle_record()

        @command('command1')
        def f():pass

        macro.record(f)
        assert macro.get_commands() == [('command1',(), {})]

        @command('command2')
        @norec
        def g():pass

        macro.record(g)
        assert macro.get_commands() == [('command1',(),{})]

    def test_run(self):
        wnd = self._getwnd("abc\ndef\n")

        macro = kaa.macro.Macro()
        macro.toggle_record()

        macro.record(wnd.document.mode.cursor_commands.right)
        macro.record(wnd.document.mode.cursor_commands.right)
        macro.record(wnd.document.mode.cursor_commands.right)
        macro.record(wnd.document.mode.cursor_commands.left)
        macro.toggle_record()

        macro.run(wnd)

        assert wnd.cursor.pos == 2

        macro.toggle_record()

        macro.record_string('123')
        macro.record_string('45')
        macro.toggle_record()

        macro.run(wnd)

        assert wnd.cursor.pos == 7
        assert wnd.document.gettext(0, 7) == 'ab12345'
