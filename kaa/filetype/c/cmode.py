from kaa.filetype.default import defaultmode
from kaa.keyboard import *
from kaa.syntax_highlight import *

CThemes = {
    'basic': []
}

c_keys = {
    (ctrl, 't'): 'toc.showlist',
}

KEYWORDS = ['asm', 'auto', 'break', 'case', 'continue', 'const', 'char',
            'default', 'do', 'double', 'else', 'endasm', 'entry', 'enum',
            'extern', 'float', 'for', 'goto', 'if', 'int', 'long', 'register',
            'return', 'short', 'signed', 'sizeof', 'static', 'struct',
            'switch', 'typedef', 'union', 'unsigned', 'void', 'volatile',
            'while']


CONSTANTS = ['NULL']


def make_tokenizer():
    return Tokenizer(tokens=[
        ("directive", SingleToken('directive', [r'\#\s*\w+'])),
        ("keyword", Keywords('keyword', KEYWORDS)),
        ("constant", Keywords('constant', CONSTANTS)),
        ("number", SingleToken('number',
                               [r'\b[0-9]+(\.[0-9]*)*\b', r'\b\.[0-9]+\b'])),
        ("comment1", Span('comment', r'/\*', '\*/', escape='\\')),
        ("comment2", Span('comment', r'//', '$', escape='\\')),

        ("string1", Span('string', '"', '"', escape='\\')),
        ("string2", Span('string', "'", "'", escape='\\')),
    ])


class CMode(defaultmode.DefaultMode):
    MODENAME = 'C'
    tokenizer = make_tokenizer()

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [c_keys])

    def init_themes(self):
        super().init_themes()
        self.themes.append(CThemes)
