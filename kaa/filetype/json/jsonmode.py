from kaa.filetype.default import defaultmode
from kaa.syntax_highlight import *

JSONThemes = {
    'basic': []
}


def make_tokenizer():
    return Tokenizer(tokens=[
        ('numeric', SingleToken('number',
                                [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])),
        ('string', Span('string', '"', '"', escape='\\'),)
    ])


class JSONMode(defaultmode.DefaultMode):
    MODENAME = 'JSON'
    tokenizer = make_tokenizer()

    def init_themes(self):
        super().init_themes()
        self.themes.append(JSONThemes)
