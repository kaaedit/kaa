import keyword
from kaa.filetype.default import defaultmode, theme
from kaa.highlight import Tokenizer, Keywords, Span
from kaa.theme import Theme, Style

PythonTheme = Theme('python', [
    Style('default', 'default', 'default', False, False),
    Style('statement', 'magenta', 'default'),
    Style('comment', 'green', 'default'),
    Style('string', 'red', 'default'),
    Style('bytes', 'blue', 'default'),
])

class PythonMode(defaultmode.DefaultMode):
    def init_theme(self):
        self.theme = PythonTheme

    def init_tokenizers(self):
        self.tokenizers = [Tokenizer([
            Keywords('python-statement', 'statement', keyword.kwlist),

            Span('python-comment', 'comment', r'\#', '$', escape='\\'),

            Span('python-string31', 'string', 'r?"""', '"""', escape='\\'),
            Span('python-string32', 'string', "r?'''", "'''", escape='\\'),
            Span('python-string11', 'string', 'r?"', '"', escape='\\'),
            Span('python-string12', 'string', "r?'", "'", escape='\\'),

            Span('python-bytes31', 'bytes', '(br?|r?b)"""', '"', escape='\\'),
            Span('python-bytes32', 'bytes', "(br?|r?b)'''", "'''", escape='\\'),
            Span('python-bytes11', 'bytes', '(br?|r?b)"', '"', escape='\\'),
            Span('python-bytes12', 'bytes', "(br?|r?b)'", "'", escape='\\'),
        ])]

