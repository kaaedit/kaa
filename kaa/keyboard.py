# key definition

import itertools
import kaa
from kaa import log
from kaa.exceptions import KaaError


class KeyBind:
    translator = None

    def __init__(self):
        self.keylist = []

    def clear(self):
        self.keylist = []

    def _split_modifier(self, key):
        mods = set()
        ch = None
        for k in key:
            if isinstance(k, Modifier):
                if k in mods:
                    raise KaaError(
                        'Multiple modifiers: {!r}'.format(key))
                mods.add(k)
            else:
                if ch is not None:
                    raise KaaError(
                        'Multiple characters: {!r}'.format(key))

                if isinstance(k, str):
                    if len(k) != 1:
                        raise KaaError(
                            'Invalid characters: {!r}'.format(key))

                ch = k

        return (mods, ch)

    def _flatten_keys(self, keys):
        if isinstance(keys, str):
            return keys

        if isinstance(keys, SpecialKey):
            return [[keys]]

        if [k for k in keys if isinstance(k, Modifier)]:
            return [keys]

        ret = []
        for k in keys:
            if isinstance(k, (list, tuple, set)):
                ret.append(k)
            elif isinstance(k, str):
                ret.extend(k)
            else:
                ret.append([k])
        return ret

    def add_keybind(self, d):
        for keys, commands in d.items():
            if isinstance(commands, str):
                commands = [commands]
            try:
                keys = self._flatten_keys(keys)
                keys = [self._split_modifier(k) for k in keys]
                keys = list(itertools.chain.from_iterable(
                    kaa.app.translate_key(mod, c) for mod, c in keys))
                self.keylist.insert(0, (keys, commands))

            except KaaError as e:
                log.warning('Failed to load key: {}'.format(e))

    def get_command(self, keys):
        for cmdkeys, commands in self.get_candidates(keys):
            if cmdkeys == keys:
                return commands

    def get_candidates(self, keys):
        for cmdkeys, commands in self.keylist:
            if keys == cmdkeys[:len(keys)]:
                yield cmdkeys, commands


class Modifier:
    keys = {}

    def __init__(self, name):
        self.name = name
        self.keys[name] = self

    def __repr__(self):
        return '<Modifier:{}>'.format(self.name)


class SpecialKey:
    keys = {}

    def __init__(self, name):
        self.name = name
        self.keys[name] = self

    def __repr__(self):
        return '<Key:{}>'.format(self.name)


shift = Modifier('shift')
ctrl = Modifier('ctrl')
alt = Modifier('alt')

backspace = SpecialKey('backspace')
pageup = SpecialKey('pageup')
pagedown = SpecialKey('pagedown')
left = SpecialKey('left')
right = SpecialKey('right')
up = SpecialKey('up')
down = SpecialKey('down')
insert = SpecialKey('insert')
delete = SpecialKey('delete')
home = SpecialKey('home')
end = SpecialKey('end')
esc = SpecialKey('esc')
tab = SpecialKey('tab')
f1 = SpecialKey('f1')
f2 = SpecialKey('f2')
f3 = SpecialKey('f3')
f4 = SpecialKey('f4')
f5 = SpecialKey('f5')
f6 = SpecialKey('f6')
f7 = SpecialKey('f7')
f8 = SpecialKey('f8')
f9 = SpecialKey('f9')
f10 = SpecialKey('f10')
f11 = SpecialKey('f11')
f12 = SpecialKey('f12')
f13 = SpecialKey('f13')
f14 = SpecialKey('f14')
f15 = SpecialKey('f15')
f16 = SpecialKey('f16')
f17 = SpecialKey('f17')
f18 = SpecialKey('f18')
f19 = SpecialKey('f19')
f20 = SpecialKey('f20')
f21 = SpecialKey('f21')
f22 = SpecialKey('f22')
f23 = SpecialKey('f23')
f24 = SpecialKey('f24')
