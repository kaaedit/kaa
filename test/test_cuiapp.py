from pytest import raises
import curses
import kaa
from kaa.cui import app
from kaa import keyboard
import kaa.options
from kaa.exceptions import KaaError


class TestKey:

    def test_keytrans(self):
        cuiapp = app.CuiApp(kaa.options.build_parser().parse_args([]))
        assert 'A' == cuiapp.translate_key((), 'A')
        assert [curses.KEY_RIGHT] == cuiapp.translate_key((), keyboard.right)
        with raises(KaaError):
            cuiapp.translate_key((), keyboard.insert)

    def test_shift(self):
        cuiapp = app.CuiApp(kaa.options.build_parser().parse_args([]))
        with raises(KaaError):
            cuiapp.translate_key({keyboard.shift}, 'A')

        assert [curses.KEY_SRIGHT] == cuiapp.translate_key(
            {keyboard.shift}, keyboard.right)

    def test_ctrl(self):
        cuiapp = app.CuiApp(kaa.options.build_parser().parse_args([]))
        assert '\x01' == cuiapp.translate_key({keyboard.ctrl}, 'a')
        assert '\x01' == cuiapp.translate_key({keyboard.ctrl}, 'A')

        with raises(KaaError):
            cuiapp.translate_key({keyboard.ctrl}, '-')

        assert [curses.KEY_SRIGHT] == cuiapp.translate_key(
            {keyboard.shift}, keyboard.right)

    def test_alt(self):
        cuiapp = app.CuiApp(kaa.options.build_parser().parse_args([]))
        assert '\x1ba' == cuiapp.translate_key({keyboard.alt}, 'a')
        assert '\x1b\x01' == cuiapp.translate_key(
            {keyboard.ctrl, keyboard.alt}, 'a')
        assert ['\x1b', curses.KEY_RIGHT] == cuiapp.translate_key(
            {keyboard.alt}, keyboard.right)
        assert ['\x1b', curses.KEY_SRIGHT] == cuiapp.translate_key(
            {keyboard.alt, keyboard.shift}, keyboard.right)
