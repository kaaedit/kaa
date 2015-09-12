import copy
from collections import namedtuple
from kaa.filetype.default import defaultmode
from kaa import doc_re
from kaa.highlight import Tokenizer, Token, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style
from kaa.command import Commands, commandid, norec, norerun
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


class LinkToken(Token):
    RE_END = doc_re.compile('^\S', doc_re.M + doc_re.X)

    def re_start(self):
        return r'\['

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.text = self.assign_tokenid(tokenizer, self.stylename)
        self.url = self.assign_tokenid(tokenizer, self.stylename)
        self.link = self.assign_tokenid(tokenizer, self.stylename)

    def get_close(self, doc, pos, chars):
        r = doc_re.compile(r'\\.|' + '|'.join('\\' + c for c in chars))
        while True:
            m = r.search(doc, pos)
            if not m:
                return '', doc.endpos()

            h = m.group()
            if h[0] == '\\':
                pos = m.end()
            else:
                return h, m.end()

    def on_start(self, tokenizer, doc, pos, match):
        f = match.start()
        c, t = self.get_close(doc, match.end(), ']')
        if t != doc.endpos():
            next = doc.gettext(t, t + 1)
            if next == ':':
                yield (f, t + 1, self.text)
                return t + 1, None, False
            elif next == ' ':
                t += 1
        yield (f, t, self.text)

        m = doc_re.compile(r'\s*(\[|\()').match(doc, t)
        if not m:
            return t, None, False

        c = m.group(1)
        if c == '[':
            c, end = self.get_close(doc, m.end(), ']')
            yield t, end, self.link
        else:
            c, end = self.get_close(doc, m.end(), '")')
            if c == '"':
                c, end = self.get_close(doc, end, '')
                c, end = self.get_close(doc, end, ')')
            yield t, end, self.url

        return end, None, False


class ImageToken(LinkToken):

    def re_start(self):
        return r'!\['


class MDInline(Span):
    WS = ' \t\r\n'

    def on_start(self, tokenizer, doc, pos, match):
        if ((pos >= doc.endpos() - 1) or
                (doc.gettext(pos + 1, pos + 2) in self.WS)):

            yield pos, pos + 1, tokenizer.nulltoken
            return pos + 1, None, False

        ret = yield from super().on_start(tokenizer, doc, pos, match)
        return ret


HEADERS = r'=-'


def build_tokenizer():
    MARKDOWNTOKENS = namedtuple('markdowntokens',
                                ['escape', 'header1', 'header2',
                                 'hr', 'link', 'image',
                                 'strong1', 'strong2',
                                 'emphasis1', 'emphasis2',
                                 'code1', 'code2', 'code3'])

    return Tokenizer(MARKDOWNTOKENS(
        # escape
        SingleToken('md-escape', 'default', [r'\\.']),

        # header
        SingleToken('md-header1', 'header',
                    [r'^.+\n(?P<H1>[{}])(?P=H1)+$'.format(HEADERS)]),
        SingleToken('md-header2', 'header', [r'^\#{1,6}.*$']),

        # hr
        SingleToken('md-hr', 'hr', [r'^(\-{3,}|_{3,}|\*{3,})$']),

        # link
        LinkToken('md-link', 'reference'),

        # image
        ImageToken('md-image', 'reference'),

        # strong
        MDInline('md-strong1', 'strong', r'\*\*', r'\*\*|$', escape='\\'),
        MDInline('md-strong2', 'strong', r'__', r'__|$', escape='\\'),

        # emphasis
        MDInline('md-emphasis1', 'emphasis', r'\*', r'\*|$', escape='\\'),
        MDInline('md-emphasis2', 'emphasis', r'_', r'_|$', escape='\\'),

        # code
        Span('md-code1', 'literal', r'^```', r'^```\s*$', escape='\\'),
        MDInline('md-code2', 'literal', r'`', r'`', escape='\\'),
        Span('md-code3', 'literal', r'^\ {4,}', r'$', escape='\\'),
    ))



class LinkToken(Span):
    def __init__(self, stylename):
        super().__init__(stylename, r'\[', r']', escape=r'\\')

    def prepare(self):
        super().prepare()

    RE_DESC_BEGIN = doc_re.compile(r'\s*\(?')
    RE_DESC = doc_re.compile(r'[")]')
    def on_start(self, doc, match):
        # [xxx](yyy "xzzzz")
        pos, terminates = yield from super().on_start(doc, match)
        if pos == doc.endpos():
            return pos, terminates

        m = self.RE_DESC_BEGIN.match(doc, pos)
        if not m:
            return pos, False
        else:
            f, t = m.span()
            c = doc.gettext(t-1, t)
            if c == '(':
                while True:
                    m = self.RE_DESC.search(doc, t)
                    if not m:
                        t = doc.endpos()
                        break
                    f, t = m.span()
                    c = doc.gettext(t-1, t)
                    if c == ')':
                        break
                    while True:
                        t = doc.findchr(t, '\\"')
                        if t == -1:
                            t = doc.endpos()
                            break
                        if doc.gettext(t, t+1) == '\\':
                            t += 2
                        else:
                            t += 1
                            break
                    

            yield (pos, t, self.styleid_span)
            return t, False

MarkdownTokenizer = Root(tokens=(
    ('escape', SingleToken('escape', [r'\\.'])),
    ('hr', SingleToken('hr', [r'^(\-{3,}|_{3,}|\*{3,})$'])),

    ('header1', SingleToken('header', [r'^.+\n(?P<H1>[-=])(?P=H1)+$'])),
    ('header2', SingleToken('header', [r'^\#{1,6}.*$'])),

    ('strong1', Span('strong', r'\*\*(?!\s)', r'\*\*|$', escape='\\')),
    ('strong2', Span('strong', r'__(?!\s)', r'__|$', escape='\\')),

    ('emphasis1', Span('emphasis', r'\*(?!\s)', r'\*|$', escape='\\')),
    ('emphasis2', Span('emphasis', r'_(?!\s)', r'_|$', escape='\\')),

    ('code1', Span('literal', r'^```', r'^```\s*$', escape='\\')),
    ('code2', Span('literal', r'^\ {4,}', r'$')),
    ('code3', Span('literal', r'`(?!\s)', r'`|$', escape='\\')),

    ('link', LinkToken('reference')),
))






MDMENU = [
    ['&Table of contents', None, 'toc.showlist'],
]

md_keys = {
    (ctrl, 't'): 'toc.showlist',
}


class MarkdownMode(defaultmode.DefaultMode):
    MODENAME = 'Markdown'

    def init_keybind(self):
        super().init_keybind()
        self.register_keys(self.keybind, [md_keys])

    def init_menu(self):
        super().init_menu()
        self.menu['CODE'] = copy.deepcopy(MDMENU)

    def init_themes(self):
        super().init_themes()
        self.themes.append(MarkdownThemes)

#    def init_tokenizers(self):
#        self.tokenizers = [build_tokenizer()]

    def init_tokenizer(self):
        self.tokenizer = MarkdownTokenizer


    HEADER1 = r'^(?P<TITLE>.+)\n(?P<H1>[{}])(?P=H1)+$'.format(HEADERS)
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
