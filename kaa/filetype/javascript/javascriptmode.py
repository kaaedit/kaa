from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import Tokenizer, Span, Keywords, EndSection
from kaa.theme import Theme, Style

JavaScriptThemes = {
    'default':
        Theme([
            # None defined
        ])
}
def build_tokenizer(stop=None, terminates=None):
    JSTOKENS = namedtuple('jstokens', ['keywords', 'comment1', 'comment2',
                       'string1', 'string2', 'stop'])

    keywords=Keywords('javasctipt-keyword', 'keyword',
         ["break", "case", "catch", "continue", "debugger", "default", "delete",
          "do", "else", "finally", "for", "function", "if", "in", "instanceof",
          "new", "return", "switch", "this", "throw", "try", "typeof", "var",
          "void", "while", "with", "class", "enum", "export", "extends", "import",
          "super", "implements", "interface", "let", "package", "private",
          "protected", "public", "static", "yield",])

    comment1=Span('javascript-comment1', 'comment', r'/\*', r'\*/', escape='\\')
    comment2=Span('javascript-comment2', 'comment', r'//', r'$', escape='\\')
    string1=Span('javascript-string1', 'string', '"', '"', escape='\\')
    string2=Span('javascript-string2', 'string', "'", "'", escape='\\')

    tokens = JSTOKENS(keywords, comment1, comment2, string1, string2, stop)

    return Tokenizer(tokens, terminates=terminates)


class JavaScriptMode(defaultmode.DefaultMode):
    MODENAME = 'JavaScript'
    def init_themes(self):
        super().init_themes()
        self.themes.append(JavaScriptThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
