from collections import namedtuple
from kaa.filetype.default import defaultmode, theme
from kaa.highlight import Tokenizer, Keywords, Span, SingleToken
from kaa.theme import Theme, Style
from gappedbuf import re as gre
from kaa.command import Commands, command, norec, norerun
from kaa.keyboard import *

CThemes = {
    'basic':
        Theme([
        ]),
}

c_keys = {
    (ctrl, 't'): 'toc.showlist',
}

def build_tokenizer(stop=None, terminates=None):
    CTOKENS = namedtuple('ctokens', 
        ['macro', 'keywords', 'number', 'comment1', 'comment2', 'string1', 
        'string2', 'stop'])

    macro = SingleToken('c-macro', 'directive', [r'\#\s*\w+'])

    keywords=Keywords('c-keyword', 'keyword',
        ['asm', 'auto', 'break', 'case', 'continue', 'const', 'char', 
         'default', 'do', 'double', 'else', 'endasm', 'entry', 'enum', 
         'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register', 
         'return', 'short', 'signed', 'sizeof', 'static', 'struct', 
         'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile', 
         'while'])

    number=SingleToken('c-numeric', 'number',
                 [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])
    comment1=Span('c-comment1', 'comment', r'/\*', r'\*/', escape='\\')
    comment2=Span('c-comment2', 'comment', r'//', r'$', escape='\\')
    string1=Span('c-string1', 'string', '"', '"', escape='\\')
    string2=Span('c-string2', 'string', "'", "'", escape='\\')

    tokens = CTOKENS(macro, keywords, number, comment1, comment2, 
        string1, string2, stop)

    return Tokenizer(tokens, terminates=terminates)


class CMode(defaultmode.DefaultMode):
    MODENAME = 'C'
    
    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [c_keys])

    def init_themes(self):
        super().init_themes()
        self.themes.append(CThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
