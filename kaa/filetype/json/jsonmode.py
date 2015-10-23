from kaa.filetype.default import defaultmode
from kaa.highlight import Tokenizer, Span, SingleToken
from kaa.syntax_highlight import *

JSONThemes = {
    'basic': []
}


def build_tokenizer():
    return Tokenizer([
        SingleToken('json-numeric', 'number',
                    [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b']),
        Span('json-string', 'string', '"', '"', escape='\\'),
    ])

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

