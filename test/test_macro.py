import kaa_testutils
from kaa.commands import editorcommand
import kaa.macro
import kaa.command
from kaa.command import commandid, norec


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

        @commandid('command1')
        def f():
            pass

        macro.record(1, f)
        assert macro.get_commands() == [
            (kaa.macro.rec_command, 1, 'command1', (), {})]

        @commandid('command2')
        @norec
        def g():
            pass

        macro.record(1, g)
        assert macro.get_commands() == [
            (kaa.macro.rec_command, 1, 'command1', (), {})]

    def test_run(self):
        wnd = self._getwnd("abc\ndef\n")

        macro = kaa.macro.Macro()
        macro.toggle_record()

        mode = wnd.document.mode
        macro.record(1, mode.get_command('cursor.right')[1])
        macro.record(1, mode.get_command('cursor.right')[1])
        macro.record(1, mode.get_command('cursor.right')[1])
        macro.record(1, mode.get_command('cursor.left')[1])
        macro.toggle_record()

        macro.run(wnd)

        assert wnd.cursor.pos == 2

        macro.toggle_record()

        macro.record_string('123', False)
        macro.record_string('45', False)
        macro.toggle_record()

        macro.run(wnd)

        assert wnd.cursor.pos == 7
        assert wnd.document.gettext(0, 7) == 'ab12345'
