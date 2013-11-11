from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import Tokenizer, Token, Span, Keywords, EndSection, SingleToken
from kaa.theme import Theme, Style

MarkdownThemes = {
    'basic':
        Theme([
            Style('header', 'Blue', None),
            Style('block', 'Orange', None),
            Style('hr', 'Green', None),
            Style('strong', 'Magenta', None),
            Style('emphasis', 'Blue', None),
            Style('literal', 'Cyan', None),
            Style('reference', 'Red', None),
            Style('role', 'Cyan', None),
            Style('substitution', 'Green', None),
        ]),
}

class LinkToken(Token):
    RE_END = gre.compile('^\S', gre.M+gre.X)
    
    def re_start(self):
        return r'\['

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.text = self.assign_tokenid(tokenizer, self.stylename)
        self.url = self.assign_tokenid(tokenizer, self.stylename)
        self.link = self.assign_tokenid(tokenizer, self.stylename)

    def get_close(self, doc, pos, chars):
        r = gre.compile(r'\\.|'+'|'.join('\\'+c for c in chars))
        while True:
            m = r.search(doc.buf, pos)
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
            next = doc.gettext(t, t+1)
            if next == ':':
                yield (f, t+1, self.text)
                return t+1, None, False
            elif next == ' ':
                t += 1
        yield (f, t, self.text)
    
        m = gre.compile(r'\s*(\[|\()').match(doc.buf, t)
        if not m:
            return t, None, False

        c = m.group(1)
        if c == '[':
            c, end = self.get_close(doc, m.end(), ']')
            yield t, end, self.link
        else:
            c, end = self.get_close(doc, m.end(), '")')
            if c == '"':
                c, end = self.get_close(doc, end, '"')
                c, end = self.get_close(doc, end, ')')
            yield t, end, self.url

        return end, None, False

class ImageToken(LinkToken):
    def re_start(self):
        return r'!\['


def build_tokenizer():
    MARKDOWNTOKENS = namedtuple('markdowntokens', 
                            ['escape', 'header1', 'header2', 'codeblock', 
                             'hr', 'link', 'image', 'strong1', 'strong2', 
                             'emphasis1', 'emphasis2', 'code1', 'code2'])

    HEADERS = r'=-'
    return Tokenizer(MARKDOWNTOKENS(
            # escape
            SingleToken('md-escape', 'default', [r'\\.']),

            # header
            SingleToken('md-header1', 'header', 
                    [r'^.+\n(?P<H1>[{}])(?P=H1)+$'.format(HEADERS)]),
            SingleToken('md-header2', 'header', [r'^\#{1,6}.*$']),

            # code block
            SingleToken('md-codeblock', 'literal', [r'^(\t+|\ {4,}).*$']),
            
            # hr
            SingleToken('md-hr', 'hr', [r'^(\-{3,}|_{3,}|\*{3,})$']),
            
            # link
            LinkToken('md-link', 'reference'),
            
            # image
            ImageToken('md-image', 'reference'),
            
            # strong
            Span('md-strong1', 'strong', r'\*\*', r'\*\*', escape='\\'),
            Span('md-strong2', 'strong', r'__', r'__', escape='\\'),

            # emphasis
            Span('md-emphasis1', 'emphasis', r'\*', r'\*', escape='\\'),
            Span('md-emphasis2', 'emphasis', r'_', r'_', escape='\\'),

            # code
            Span('md-code1', 'literal', r'``', r'``', escape='\\'),
            Span('md-code2', 'literal', r'`', r'`', escape='\\'),
        ))




class MarkdownMode(defaultmode.DefaultMode):
    MODENAME = 'Markdown'
    def init_themes(self):
        super().init_themes()
        self.themes.append(MarkdownThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]
