from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import Tokenizer, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style

DiffThemes = {
    'default':
        Theme([
            Style('fromfile', 'Red', 'default'),
            Style('tofile', 'Cyan', 'default'),
            Style('hunk', 'Blue', 'default'),
            Style('add', 'Green', 'default'),
            Style('remove', 'Magenta', 'default'),
            Style('header', 'Yellow', 'default'),
        ])
}


class DiffMode(defaultmode.DefaultMode):
    MODENAME = 'Diff'
    def init_themes(self):
        super().init_themes()
        self.themes.append(DiffThemes)

    def init_tokenizers(self):
        self.tokenizers = [Tokenizer([
            Span('diff-fromfile', 'fromfile', r'^---', '$'),
            Span('diff-tofile', 'tofile', r'^\+\+\+', '$'),
            Span('diff-hunk', 'hunk', r'^@@', '@@'),
            Span('diff-add', 'add', r'^\+', '$'),
            Span('diff-remove', 'remove', r'^-', '$'),
            Span('diff-header', 'header', r'^\S+', '$'),
        ])]
