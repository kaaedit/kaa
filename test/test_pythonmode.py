from unittest.mock import patch
import kaa_testutils
from kaa.filetype.python import pythonmode


class TestPythonMode(kaa_testutils._TestScreenBase):
    DEFAULTMODECLASS = pythonmode.PythonMode

    def test_get_headers(self):
        script = '''
class spam:
    def ham(self, \, x=(def xxx)):
        'def'
# class xyz
def egg():
   """\\\\"""
def bacon():
'''
        doc = self._getdoc(script)
        tokens = [t for t in doc.mode.get_headers()]
        assert tokens == [
            ('namespace', None, 'spam', 'spam', None, 1),
            ('function', tokens[0], 'spam.ham', 'ham()', None, 13),
            ('function', None, 'egg', 'egg()', None, 74),
            ('function', None, 'bacon', 'bacon()', None, 97)]

    def test_pyindent(self):
        # test block begins
        script = '''
abc:
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=5):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\nabc:\n    \n'

        # test un-closed parenthesis
        script = '''
abc(
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=5):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\nabc(\n    \n'

        # test balanced parenthesis
        script = '''
abc()
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=6):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\nabc()\n\n'

        # test closed parenthesis
        script = '''
  abc
    abc)
'''

        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=15):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\n  abc\n    abc)\n    \n'

        # test closed parenthesis, but no dedent required
        script = '''
  abc
  )
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=10):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\n  abc\n  )\n  \n'

        # test comment
        script = '''
abc#(
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=6):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\nabc#(\n\n'

        # test string
        script = '''
abc"(
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=6):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\nabc"(\n\n'

        # test string closed
        script = '''
abc"""-"""(
'''
        wnd = self._getwnd(script)
        with patch.object(wnd.cursor, 'pos', new=12):
            wnd.document.mode.on_auto_indent(wnd)
        assert wnd.document.gettext(0, wnd.document.endpos()
                                    ) == '\nabc"""-"""(\n    \n'
