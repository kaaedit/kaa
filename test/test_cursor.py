from contextlib import ExitStack
from unittest.mock import patch
from kaa import cursor

import kaa_testutils


class TestCursor(kaa_testutils._TestScreenBase):

    def _getcursor(self, s, width=10, height=10):
        wnd = self._getwnd(s, width, height)
        return cursor.Cursor(wnd)

    def test_up(self):
        cursor = self._getcursor("abc\ndef\nghi\n012\n345\n678\n", height=3)
        cursor.preferred_col = 2

        cursor.setpos(10)
        assert cursor.up()
        assert cursor.pos == 6

        assert cursor.up()
        assert cursor.pos == 2

        assert not cursor.up()
        assert cursor.pos == 2

        cursor.setpos(24)
        assert cursor.up()
        assert cursor.pos == 22

        assert cursor.up()
        assert cursor.pos == 18

    def test_down(self):
        cursor = self._getcursor("abc\ndef\nghi\n012\n345\n678\n", height=3)
        cursor.preferred_col = 10

        cursor.setpos(0)
        assert cursor.down()
        assert cursor.pos == 7

        assert cursor.down()
        assert cursor.pos == 11

        cursor.setpos(16)
        assert cursor.down()
        assert cursor.pos == 23

        assert cursor.down()
        assert cursor.pos == 24

    def test_right(self):
        s = "abc\ndef\nghi\n012\n345\n678\n"
        cursor = self._getcursor(s, height=1)
        cursor.setpos(0)
        for i in range(len(s)):
            cursor.right()
            assert cursor.pos == i + 1

    def test_rightword(self):
        s = 'abc あいうえおカキクケコ'
        cursor = self._getcursor(s, height=1, width=30)
        cursor.setpos(0)

        cursor.right(word=True)
        assert cursor.pos == 4

        cursor.right(word=True)
        assert cursor.pos == 9

        cursor.right(word=True)
        assert cursor.pos == 14

    def test_left(self):
        s = "abc\ndef\nghi\n012\n345\n678\n"
        cursor = self._getcursor(s, height=1)
        cursor.setpos(len(s))
        for i in range(len(s) - 1, -1, -1):
            cursor.left()
            assert cursor.pos == i

    def test_leftword(self):
        s = 'abc あいうえおカキクケコ'
        cursor = self._getcursor(s, height=1, width=30)
        cursor.setpos(len(s))

        cursor.left(word=True)
        assert cursor.pos == 9

        cursor.left(word=True)
        assert cursor.pos == 4

        cursor.left(word=True)
        assert cursor.pos == 0

    def test_pagedown(self):
        s = "abc\ndef\nghi\n012\n345\n678\n"
        cursor = self._getcursor(s, height=3)
        cursor.setpos(0)
        cursor.preferred_col = 1

        cursor.pagedown()
        assert cursor.pos == 9

        cursor.pagedown()
        assert cursor.pos == 17

        cursor.pagedown()
        assert cursor.pos == 24

    def test_pageup(self):
        s = "abc\ndef\nghi\n012\n345\n678\n"
        cursor = self._getcursor(s, height=3)
        cursor.setpos(24)
        cursor.preferred_col = 1

        cursor.pageup()
        assert cursor.pos == 17

        cursor.pageup()
        assert cursor.pos == 9

        cursor.pageup()
        assert cursor.pos == 5
