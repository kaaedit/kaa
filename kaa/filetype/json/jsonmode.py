from kaa.filetype.default import defaultmode
from kaa.highlight import Tokenizer, Span, SingleToken

JSONThemes = {
    'basic': []
}


def build_tokenizer():
    return Tokenizer([
        SingleToken('json-numeric', 'number',
                    [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b']),
        Span('json-string', 'string', '"', '"', escape='\\'),
    ])


class JSONMode(defaultmode.DefaultMode):
    MODENAME = 'JSON'

    def init_themes(self):
        super().init_themes()
        self.themes.append(JSONThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
