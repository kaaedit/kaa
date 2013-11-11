from kaa.filetype.default import defaultmode
from kaa.highlight import Tokenizer, Span
from kaa.theme import Theme, Style

DiffThemes = {
    'basic':
        Theme([
            Style('default', 'Base00', None),
            Style('fromfile', 'Orange', None),
            Style('tofile', 'Yellow', None),
            Style('hunk', 'Blue', None),
            Style('remove', 'Orange', None, bold=True),
            Style('add', 'Yellow', None, bold=True),
            Style('header', 'Orange', None),
        ]),
}

def build_tokenizer():
    return Tokenizer([
            Span('diff-fromfile', 'fromfile', r'^---', '$'),
            Span('diff-tofile', 'tofile', r'^\+\+\+', '$'),
            Span('diff-hunk', 'hunk', r'^@@', '@@'),
            Span('diff-add', 'add', r'^\+', '$'),
            Span('diff-remove', 'remove', r'^-', '$'),
            Span('diff-header', 'header', r'^\S+', '$'),
        ])

class DiffMode(defaultmode.DefaultMode):
    MODENAME = 'Diff'
    def init_themes(self):
        super().init_themes()
        self.themes.append(DiffThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
