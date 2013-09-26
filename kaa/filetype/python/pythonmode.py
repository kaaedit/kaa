import keyword
from kaa.filetype.default import defaultmode, theme
from kaa.highlight import Tokenizer, Keywords, Span
from kaa.theme import Theme, Style
from gappedbuf import re as gre

PythonThemes = {
    'default':
        Theme([
            Style('python-bytes', 'blue', 'default'),
        ])
}

class PythonMode(defaultmode.DefaultMode):
    def init_themes(self):
        super().init_themes()
        self.themes.append(PythonThemes)

    def init_tokenizers(self):
        self.tokenizers = [Tokenizer([
            Keywords('python-statement', 'keyword', keyword.kwlist),

            Span('python-comment', 'comment', r'\#', '$', escape='\\'),

            Span('python-string31', 'string', 'r?"""', '"""', escape='\\'),
            Span('python-string32', 'string', "r?'''", "'''", escape='\\'),
            Span('python-string11', 'string', 'r?"', '"', escape='\\'),
            Span('python-string12', 'string', "r?'", "'", escape='\\'),

            Span('python-bytes31', 'python-bytes', '(br?|r?b)"""', '"', escape='\\'),
            Span('python-bytes32', 'python-bytes', "(br?|r?b)'''", "'''", escape='\\'),
            Span('python-bytes11', 'python-bytes', '(br?|r?b)"', '"', escape='\\'),
            Span('python-bytes12', 'python-bytes', "(br?|r?b)'", "'", escape='\\'),
        ])]

