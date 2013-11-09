from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import Tokenizer, Token, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style

RstThemes = {
    'default':
        Theme([
            Style('header', 'Blue', None),
            Style('block', 'Orange', None),
            Style('directive', 'Green', None),
            Style('table', 'Base0', None),
            Style('strong', 'Magenta', None),
            Style('emphasis', 'Blue', None),
            Style('literal', 'Cyan', None),
            Style('reference', 'Red', None),
            Style('role', 'Cyan', None),
            Style('substitution', 'Green', None),
        ])
}

class RstInline(Span):
    WS = ' \t\r\n'
    STARTS = '\'"([{<' + WS
    ENDS = '\'".,:;!?-)]}/\\>' + WS
    def on_start(self, tokenizer, doc, pos, match):
        if pos and (doc.gettext(pos-1, pos) not in self.STARTS):
            yield pos, pos+1, tokenizer.nulltoken
            return pos+1, None, False
                
        ret = yield from  super().on_start(tokenizer, doc, pos, match)
        return ret

    def _is_end(self, doc, m):
        pos = m.end()
        if pos < doc.endpos():
            return (doc.gettext(pos, pos+1) in self.ENDS)
        return True
        

def build_tokenizer():
    RSTTOKENS = namedtuple('rsttokens', 
                            ['escape', 'header1', 'header2', 'star', 
                             'directive', 'block', 'tableborder',
                             'tablerow',
                             'strong', 'emphasis', 
                             'literal', 'interpreted', 'reference',  
                             'role',
                             'target', 'substitution', 'citation',
                         ])

    HEADERS = r'=\-`:\'"~^_*+#<>'
    return Tokenizer(
            RSTTOKENS(
            # escape
            SingleToken('escape', 'default', [r'\\.']),
            
            # header token
            SingleToken('header1', 'header', 
                    [r'^(?P<H>[{}])(?P=H)+\n.+\n(?P=H)+$'.format(HEADERS)]),
            SingleToken('header2', 'header', 
                    [r'^.+\n(?P<H2>[{}])(?P=H2)+$'.format(HEADERS)]),

            # list
            Span('rst-star', 'default', r'^\s*\*\s+', r'$', escape='\\'),

            # block
            Span('directive', 'directive', r'\.\.\s+\S+::', '^\S', 
                escape='\\', capture_end=False),
            Span('block', 'block', r'::\s*$', '^\S', escape='\\', 
                capture_end=False),

            #table
            SingleToken('rst-table-border', 'table', [r'^\+[+-=]+$']),
            SingleToken('rst-table-row', 'table', [r'\|\s+']),
            
            # inline token
            RstInline('rst-strong', 'strong', r'\*\*', r'\*\*', escape='\\'),
            RstInline('rst-emphasis', 'emphasis', r'\*', r'\*', escape='\\'),
            RstInline('rst-literal', 'literal', r'``', r'``', escape='\\'),
            RstInline('rst-interpreted', 'reference', r'`', r'`_?_?', 
                    escape='\\'),
            SingleToken('rst-reference', 'reference', 
                    [r'\b[a-zA-Z0-9]+__?\b']),
            RstInline('rst-role', 'role', r':[a-zA-Z0-9]+:`', r'`', 
                escape='\\'),
            RstInline('rst-target', 'reference', r'_`\w', r'`', escape='\\'),
            SingleToken('rst-substitution', 'substitution', [r'\|\w+\|']),
            SingleToken('rst-citation', 'reference', [r'\[\w+\]_\b']),

        ))

class RstMode(defaultmode.DefaultMode):
    MODENAME = 'Rst'
    def init_themes(self):
        super().init_themes()
        self.themes.append(RstThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
