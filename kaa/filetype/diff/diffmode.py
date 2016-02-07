from kaa.filetype.default import defaultmode
from kaa.theme import Style
from kaa.syntax_highlight import *

DiffThemes = {
    'basic': [
        Style('default', 'Base00', None),
        Style('fromfile', 'Orange', None),
        Style('tofile', 'Yellow', None),
        Style('hunk', 'Blue', None),
        Style('remove', 'Orange', None, bold=True),
        Style('add', 'Yellow', None, bold=True),
        Style('header', 'Orange', None),
    ],
}


def make_tokenizer():
    return Tokenizer(tokens=[
        ('fromfile', Span('fromfile', r'^---', '$')),
        ('tofile', Span('tofile', r'^\+\+\+', '$')),
        ('hunk', Span('hunk', r'^@@', '@@')),
        ('add', Span('add', r'^\+', '$')),
        ('remove', Span('remove', r'^-', '$')),
        ('header', Span('header', r'^\S+', '$')),
    ])


class DiffMode(defaultmode.DefaultMode):
    MODENAME = 'Diff'
    tokenizer = make_tokenizer()

    def init_themes(self):
        super().init_themes()
        self.themes.append(DiffThemes)
