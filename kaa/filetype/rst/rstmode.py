import unicodedata
import copy
from kaa.filetype.default import defaultmode
from kaa import doc_re
from kaa.theme import Style
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa.keyboard import *
from kaa.syntax_highlight import *

RstThemes = {
    'basic': [
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
    ],
}


def _build_seps():
    starts = []
    ends = []

    for i in range(0x12000):
        c = chr(i)
        category = unicodedata.category(c)
        if category in {'Pd', 'Po', 'Ps', 'Pi', 'Pf'}:
            starts.append(c)
        if category in {'Pd', 'Po', 'Pe', 'Pi', 'Pf'}:
            ends.append(c)
    return ''.join(starts), ''.join(ends)

SEP_STARTS, SEP_ENDS = _build_seps()


class RstInline(Span):
    WS = ' \t\r\n'
    STARTS = '\'"([{<' + WS + SEP_STARTS
    ENDS = '\'".,:;!?-)]}/\\>' + WS + SEP_ENDS

    def on_start(self, doc, match):
        pos = match.start()
        if ((pos and (doc.gettext(pos - 1, pos) not in self.STARTS)) or
                (pos >= doc.endpos() - 1) or
                (doc.gettext(pos + 1, pos + 2) in self.WS)):

            yield pos, pos + 1, self.tokenizer.styleid_default
            return pos + 1, self.terminates

        ret = yield from super().on_start(doc, match)
        return ret

    def _is_span_end(self, doc, m):
        pos = m.end()
        if pos < doc.endpos():
            return (doc.gettext(pos, pos + 1) in self.ENDS)
        return True


class TableToken(SingleToken):

    def on_start(self, doc, match):
        in_table = False
        pos = match.start()
        tol = doc.gettol(pos)
        if pos == tol:
            in_table = True
        else:
            # check if previous line is table
            if tol > 1:
                token = self.tokenizer.get_token_at(doc, tol - 2)
                if isinstance(token, TableToken):
                    in_table = True
        if in_table:
            ret = yield from super().on_start(doc, match)
            return ret
        else:
            yield pos, pos + 1, self.tokenizer.styleid_default
            return pos + 1, self.terminates


RST_HEADERS = r'=\-`:\'"~^_*+#<>'


def make_tokenizer():
    return Tokenizer(tokens=[
        # escape
        ('escape', SingleToken('default', [r'\\.'])),

        # header token
        ('header1', SingleToken('header',
                                [r'^(?P<H>[{}])(?P=H)+\n.+\n(?P=H)+$'.format(RST_HEADERS)])),
        ('header2', SingleToken('header',
                                [r'^.+\n(?P<H2>[{}])(?P=H2)+$'.format(RST_HEADERS)])),

        # block
        ('directive', Span('directive', r'\.\.\s+\S+::', '^\S',
                           escape='\\', capture_end=False)),
        ('block', Span('block', r'::', '^\S', capture_end=False)),

        # table
        ('table_border', TableToken('table', [r'\+[+\-=]+(\s+|$)'])),
        ('table_row', TableToken('table', [r'\|(\s+|$)'])),

        # inline token
        ('strong', RstInline('strong',
                             r'\*\*', r'\*\*', escape='\\')),
        ('emphasis', RstInline('emphasis',
                               r'\*', r'\*', escape='\\')),
        ('literal', RstInline('literal', r'``', r'``', escape='')),
        ('interpreted', RstInline('reference', r'`', r'`_?_?',
                                  escape='\\')),
        ('reference', SingleToken('reference',
                                  [r'\b[a-zA-Z0-9]+__?\b'])),
        ('role', RstInline('role', r':[a-zA-Z0-9]+:`', r'`',
                           escape='\\')),
        ('target', RstInline('reference',
                             r'_`\w', r'`', escape='\\')),
        ('substitution', SingleToken('substitution', [r'\|\w+\|'])),
        ('citation', SingleToken('reference', [r'\[\w+\]_\b'])),
    ])


RSTMENU = [
    ['&Table of contents', None, 'toc.showlist'],
]

rst_keys = {
    (ctrl, 't'): 'toc.showlist',
}


class RstMode(defaultmode.DefaultMode):
    MODENAME = 'Rst'
    tokenizer = make_tokenizer()

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [rst_keys])

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(RSTMENU)

    def init_themes(self):
        super().init_themes()
        self.themes.append(RstThemes)

    HEADER1 = r'''^(?P<H>[{}])(?P=H)+\n
                  (?P<TITLE>.+)\n
                  (?P=H)+$'''.format(RST_HEADERS)

    HEADER2 = r'''^(?P<TITLE2>.+)\n
                (?P<H2>[{}])(?P=H2)+$'''.format(RST_HEADERS)

    RE_HEADER = doc_re.compile(
        '|'.join([HEADER1, HEADER2]), doc_re.X | doc_re.M)

    def get_headers(self):
        levels = {}
        stack = []
        pos = 0
        while True:
            m = self.RE_HEADER.search(self.document, pos)
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
                                         None, m.start())
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
                name, None, m.start())
            yield header
            stack.append((level, header))

    @commandid('toc.showlist')
    @norec
    @norerun
    def show_toclist(self, wnd):
        from kaa.ui.toclist import toclistmode
        headers = list(self.get_headers())
        toclistmode.show_toclist(wnd, headers)
