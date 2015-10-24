from unittest.mock import patch

import kaa
from kaa.ui.dialog import dialogmode
from kaa.theme import Theme, Style

import kaa_testutils


class TestDialogCursor(kaa_testutils._TestScreenBase):

    def _getcursor(self, s):
        wnd = self._getwnd(s)
        return dialogmode.DialogCursor(wnd, [dialogmode.MarkRange('mark1'), dialogmode.MarkRange('mark2')])

    def test_cursorrange(self):
        cursor = self._getcursor("0123456789")
        cursor.wnd.document.marks['mark1'] = (1, 3)
        cursor.wnd.document.marks['mark2'] = (5, 10)

        cursor.setpos(1)
        cursor.left()
        assert cursor.pos == 1
        cursor.right()
        assert cursor.pos == 2
        cursor.right()
        assert cursor.pos == 3
        cursor.right()
        assert cursor.pos == 3

        cursor.setpos(5)
        cursor.left()
        assert cursor.pos == 5
        cursor.setpos(10)
        cursor.right()
        assert cursor.pos == 10


class TestFormBuilder(kaa_testutils._TestScreenBase):

    def _getmodeclass(self):
        return dialogmode.DialogMode

    def test_build(self):
        doc = self._getdoc('')

        f = dialogmode.FormBuilder(doc)
        f.append_text('default', 'abc')

        assert doc.gettext(0, doc.endpos()) == 'abc'
        assert doc.styles.getints(0, doc.endpos()) == [0] * doc.endpos()

    def test_build_mark(self):
        doc = self._getdoc('')

        f = dialogmode.FormBuilder(doc)
        f.append_text('default', 'abc', 'mark1', 'mark2')
        f.append_text('default', 'def', 'mark3', 'mark4')

        assert doc.gettext(doc.marks['mark3'], doc.marks['mark4']) == 'def'

    def test_build_shortcut(self):
        kaa.app.DEFAULT_THEME = 'basic'

        doc = self._getdoc('')

        doc.mode.themes = [{'basic': [
            Style('default', 'default', 'default', False, False),
            Style('shortcut', 'default', 'default', False, False),
        ]}]
        doc.mode._build_theme()

        f = dialogmode.FormBuilder(doc)

        def cb(wnd):
            pass
        f.append_text('default', 'ab&cdef', on_shortcut=cb,
                      shortcut_style='shortcut', shortcut_mark='mark1')

        assert doc.gettext(0, doc.endpos()) == 'abcdef'

        id1 = doc.mode.get_styleid('default')
        id2 = doc.mode.get_styleid('shortcut')
        assert doc.styles.getints(
            0, doc.endpos()) == [id1, id1, id2, id1, id1, id1]
        assert doc.marks['mark1'] == 2
