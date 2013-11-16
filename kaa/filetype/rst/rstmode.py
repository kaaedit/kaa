import copy
from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import Tokenizer, Token, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style
from kaa.command import Commands, command, norec, norerun
from kaa.keyboard import *

RstThemes = {
    'basic':
        Theme([
            Style('header', 'Blue', None),
            Style('block', 'Orange', None),
            Style('directive', 'Green', None),
            Style('table', 'Cyan', None),
            Style('strong', 'Magenta', None),
            Style('emphasis', 'Blue', None),
            Style('literal', 'Cyan', None),
            Style('reference', 'Red', None),
            Style('role', 'Cyan', None),
            Style('substitution', 'Green', None),
        ]),
}

class RstInline(Span):
    WS = ' \t\r\n'
    STARTS = '\'"([{<' + WS
    ENDS = '\'".,:;!?-)]}/\\>' + WS
    
    def on_start(self, tokenizer, doc, pos, match):
        if ((pos and (doc.gettext(pos-1, pos) not in self.STARTS)) or 
            (pos >= doc.endpos()-1) or
            (doc.gettext(pos+1, pos+2) in self.WS)):

            yield pos, pos+1, tokenizer.nulltoken
            return pos+1, None, False
                
        ret = yield from super().on_start(tokenizer, doc, pos, match)
        return ret

    def _is_end(self, doc, m):
        pos = m.end()
        if pos < doc.endpos():
            return (doc.gettext(pos, pos+1) in self.ENDS)
        return True
        

class TableToken(SingleToken):
    def on_start(self, tokenizer, doc, pos, match):
        in_table = False
        tol = doc.gettol(pos)
        if pos == tol:
            in_table = True
        else:
            # check if previous line is table
            if tol > 1:
                laststyle = doc.getstyles(tol-2, tol-1)[0]
                token = tokenizer.highlighter.get_token(laststyle)
                if isinstance(token, TableToken):
                    in_table = True
        if in_table:
            ret = yield from super().on_start(tokenizer, doc, pos, match)
            return ret
        else:
            yield pos, pos+1, tokenizer.nulltoken
            return pos+1, None, False
    

RST_HEADERS = r'=\-`:\'"~^_*+#<>'
def build_tokenizer():
    RSTTOKENS = namedtuple('rsttokens', 
                            ['escape', 'header1', 'header2', 
                             'directive', 'block', 'tableborder',
                             'tablerow',
                             'strong', 'emphasis', 
                             'literal', 'interpreted', 'reference',  
                             'role',
                             'target', 'substitution', 'citation',
                         ])

    return Tokenizer(
            RSTTOKENS(
            # escape
            SingleToken('escape', 'default', [r'\\.']),
            
            # header token
            SingleToken('header1', 'header', 
                [r'^(?P<H>[{}])(?P=H)+\n.+\n(?P=H)+$'.format(RST_HEADERS)]),
            SingleToken('header2', 'header', 
                [r'^.+\n(?P<H2>[{}])(?P=H2)+$'.format(RST_HEADERS)]),

            # block
            Span('directive', 'directive', r'\.\.\s+\S+::', '^\S', 
                escape='\\', capture_end=False),
            SingleToken('block', 'block', [r'::[\ \t]*$']),

            #table
            TableToken('rst-table-border', 'table', [r'\+[+\-=]+(\s+|$)']),
            TableToken('rst-table-row', 'table', [r'\|(\s+|$)']),
            
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


RSTMENU = [
    ['&Table of contents', None, 'toc.showlist'],
]

rst_keys = {
    (ctrl, 't'): 'toc.showlist',
}

class RstMode(defaultmode.DefaultMode):
    MODENAME = 'Rst'

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [rst_keys])

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(RSTMENU)

    def init_themes(self):
        super().init_themes()
        self.themes.append(RstThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]

    HEADER1 = r'''^(?P<H>[{}])(?P=H)+\n
                  (?P<TITLE>.+)\n
                  (?P=H)+$'''.format(RST_HEADERS)

    HEADER2 = r'''^(?P<TITLE2>.+)\n
                (?P<H2>[{}])(?P=H2)+$'''.format(RST_HEADERS)
    
    RE_HEADER = gre.compile('|'.join([HEADER1, HEADER2]), gre.X|gre.M)

    def get_headers(self):
        levels = {}
        stack = []
        pos = 0
        while True:
            m = self.RE_HEADER.search(self.document.buf, pos)
            if not m:
                break
    
            pos = m.end()
            name = m.group('TITLE') or m.group('TITLE2')
            name = name.strip()

            bar = (m.group('H'), m.group('H2'))
            if bar not in levels:
                level = len(levels)
                levels[bar] = level
            else:
                level = levels[bar]

            if not stack:
                header = self.HeaderInfo('namespace', None, name, name, 
                            None, pos)
                yield header
                stack.append((level, header))
                continue

            for i, (parent_level, info) in enumerate(stack):
                if level <= parent_level:
                    del stack[i:]
                    break

            if stack:
                parent = stack[-1][1]
            else:
                parent = None

            header = self.HeaderInfo(
                'namespace', parent, name, 
                name, None, pos)
            yield header
            stack.append((level, header))
            

    @command('toc.showlist')
    @norec
    @norerun
    def show_toclist(self, wnd):
        from kaa.ui.toclist import toclistmode
        headers = list(self.get_headers())
        toclistmode.show_toclist(wnd, headers)

