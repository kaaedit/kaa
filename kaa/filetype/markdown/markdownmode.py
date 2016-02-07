import copy
from kaa.filetype.default import defaultmode
from kaa import doc_re
from kaa.theme import Style
from kaa.command import commandid
from kaa.command import norec
from kaa.command import norerun
from kaa.keyboard import *
from kaa.syntax_highlight import *


MarkdownThemes = {
    'basic': [
        Style('escape', 'default', 'default'),
        Style('header', 'Blue', None),
        Style('hr', 'Green', None),
        Style('strong', 'Magenta', None),
        Style('emphasis', 'Blue', None),
        Style('literal', 'Cyan', None),
        Style('reference', 'Red', None),
        Style('role', 'Cyan', None),
        Style('substitution', 'Green', None),
    ],
}


class LinkToken(Span):
    # [xxx](yyy "xzzzz")
    # [xxx]:
    # ![xxx]

    def __init__(self, stylename):
        super().__init__(stylename, r'!?\[', r'][:\(]?', escape=r'\\')

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if pos == doc.endpos():
            return pos, terminates
        c = doc.gettext(pos - 1, pos)

        if c == '(':
            # [xxx](yyy "xzzzz")
            pos = yield from self.tokenizer._LinkTokenizer.run(doc, pos)

        return pos, False


def is_list_block(doc, pos, tokenizer):
    '''Returns True if pos is in list block'''

    pos = doc.gettol(pos)
    while pos:
        pos -= 1
        tol = doc.gettol(pos)
        s = doc.gettext(tol, pos).rstrip()
        if not s:
            # skip blank line
            continue
        token = tokenizer.get_token_at(doc, tol)
        if token is tokenizer.tokens.list:
            return True

        if s[0] not in ['\t ']:  # check previous line if indended.
            break
        pos = tol


class List(SingleToken):

    def on_start(self, doc, match):
        if match.group('list_indent'):
            # has indent
            f, t = match.span()
            if not is_list_block(doc, f, self.tokenizer):
                t = doc.geteol(f)
                yield (f, t, self.tokenizer.tokens.code1.styleid_span)
                return t, self.terminates

        ret = yield from super().on_start(doc, match)
        return ret


class PreBlock(Span):

    def on_start(self, doc, match):
        # skip if line is nested list block
        #
        # 1. abcdefg
        #     2. hijklmn

        if is_list_block(doc, match.start(), self.tokenizer):
            f, t = match.span(1)
            yield (f, t, self.tokenizer.styleid_default)
            return t, self.terminates

        ret = yield from super().on_start(doc, match)
        return ret


def make_tokenizer():
    ret = Tokenizer(tokens=(
        ('escape', SingleToken('escape', [r'\\.'])),
        ('hr', SingleToken('hr', [r'^(\-{3,}|_{3,}|\*{3,})$'])),

        ('header1', SingleToken('header', [r'^.+\n(?P<H1>[-=])(?P=H1)+$'])),
        ('header2', SingleToken('header', [r'^\#{1,6}.*$'])),

        ('strong1', Span('strong', r'\*\*(?!\s)', r'\*\*|$', escape='\\')),
        ('strong2', Span('strong', r'__(?!\s)', r'__|$', escape='\\')),

        ('emphasis1', Span('emphasis', r'\*(?!\s)', r'\*|$', escape='\\')),
        ('emphasis2', Span('emphasis', r'_(?!\s)', r'_|$', escape='\\')),

        ('list', List('default', [r'^(?P<list_indent>\s*)(\*\ |\d+\.\ )'])),
        ('code1', PreBlock('literal', r'^(\ {4,})', r'$')),
        ('code2', Span('literal', r'^```', r'^```\s*$', escape='\\')),
        ('code3', Span('literal', r'`(?!\s)', r'`|$', escape='\\')),

        ('link', LinkToken('reference')),
    ))

    ret._LinkTokenizer = Tokenizer(parent=ret,
                                   default_style='reference',
                                   tokens=(
                                       ('desc',
                                        Span('reference', r'"', r'"', escape='\\')),
                                       ('close',
                                        SingleToken(
                                            'reference', [r"\)"], terminates=True)),
                                   ))
    return ret


MDMENU = [
    ['&Table of contents', None, 'toc.showlist'],
]

md_keys = {
    (ctrl, 't'): 'toc.showlist',
}


class MarkdownMode(defaultmode.DefaultMode):
    MODENAME = 'Markdown'
    tokenizer = make_tokenizer()

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [md_keys])

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(MDMENU)

    def init_themes(self):
        super().init_themes()
        self.themes.append(MarkdownThemes)

    def init_tokenizer(self):
        self.tokenizer = MarkdownTokenizer

    HEADER1 = r'^(?P<TITLE>.+)\n(?P<H1>[=-])(?P=H1)+$'
    HEADER2 = r'^(?P<H2>\#{1,6})(?P<TITLE2>.+)$'

    RE_HEADER = doc_re.compile(
        '|'.join([HEADER1, HEADER2]), doc_re.X | doc_re.M)

    def get_headers(self):
        stack = []
        pos = 0
        while True:
            m = self.RE_HEADER.search(self.document, pos)
            if not m:
                break

            pos = m.end()
            name = m.group('TITLE') or m.group('TITLE2')
            name = name.strip()

            bar = m.group('H1')
            if bar:
                if bar == '=':
                    level = 0
                else:
                    level = 1
            else:
                level = len(m.group('H2')) - 1

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
