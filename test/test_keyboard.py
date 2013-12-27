from unittest.mock import patch
import kaa_testutils
from kaa import keyboard
from kaa.keyboard import *


class TestKeyBind:

    def _create_keybind(self, bind):

        kb = keyboard.KeyBind()
        kb.add_keybind(bind)

        return kb

    def test_char(self):
        kb = self._create_keybind({
            'a': 'command'
        })

        assert kb.keylist == [
            ([set(), 'a'], ['command']),
        ]

        kb = self._create_keybind({
            'aa': 'command'
        })

        assert kb.keylist == [
            ([set(), 'a', set(), 'a'], ['command']),
        ]

    def test_special(self):
        kb = self._create_keybind({
            right: 'command'
        })

        assert kb.keylist == [
            ([set(), right], ['command']),
        ]

        kb = self._create_keybind({
            (right, left): 'command'
        })

        assert kb.keylist == [
            ([set(), right, set(), left], ['command']),
        ]

        kb = self._create_keybind({
            ((right,), (left,)): 'command'
        })

        assert kb.keylist == [
            ([set(), right, set(), left, ], ['command']),
        ]

    def test_mix(self):

        kb = self._create_keybind({
            ((right,), 'a'): 'command'
        })

        assert kb.keylist == [
            ([set(), right, set(), 'a'], ['command']),
        ]

        kb = self._create_keybind({
            (right, 'a'): 'command'
        })

        assert kb.keylist == [
            ([set(), right, set(), 'a'], ['command']),
        ]

        kb = self._create_keybind({
            ((right,), 'ab', left): 'command'
        })

        assert kb.keylist == [
            ([set(), right, set(), 'a', set(), 'b', set(), left], ['command']),
        ]

    def test_modifier(self):
        kb = self._create_keybind({
            ('a', ctrl): 'command'
        })

        assert kb.keylist == [
            ([set([ctrl]), 'a'], ['command']),
        ]

        kb = self._create_keybind({
            (('a', ctrl), ('b', ctrl)): 'command'
        })

        assert kb.keylist == [
            ([set([ctrl]), 'a', set([ctrl]), 'b'], ['command']),
        ]

        kb = self._create_keybind({
            (ctrl, shift, right): 'command'
        })

        assert kb.keylist == [
            ([set([ctrl, shift]), right], ['command']),
        ]

        kb = self._create_keybind({
            ((ctrl, right), (ctrl, 'b')): 'command'
        })

        assert kb.keylist == [
            ([set([ctrl]), right, set([ctrl]), 'b'], ['command']),
        ]

    def test_callable(self):

        def f(wnd):
            pass

        kb = self._create_keybind({
            ((right,), 'a'): f
        })

        assert kb.keylist == [
            ([set(), right, set(), 'a'], f),
        ]
