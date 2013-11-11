from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import Tokenizer, Span, SingleToken, Token, SubSection, EndSection
from kaa.theme import Theme, Style
from kaa.filetype.javascript import javascriptmode

CSSThemes = {
    'basic':
        Theme([
            Style('css-selector', 'magenta', 'default'),
            Style('css-propname', 'blue', 'default', bold=True),
            Style('css-propvalue', 'green', 'default', bold=True),
    ]),
}

class CSSProp(Token):
    def __init__(self, name, stylename, close='', closestyle=None):
        super().__init__(name, stylename)

        self.close = self.closestyle = ''
        if close:
            self.close = '(?P<CLOSE>{})|'.format(close)
            self.closestyle = closestyle

        self.CSS_TOP = gre.compile(self.close + r'(?P<COMMENT>/\*)|(?P<STRING>[\'"])|({)')
        self.END_COMMENT = gre.compile(r'\*/')
        self.PROPERTY_TOP = gre.compile(self.close + r'(?P<COMMENT>/\*)|(?P<STRING>[\'"])|:|}')
        self.PROPERTY_VALUE = gre.compile(self.close + r'(?P<COMMENT>/\*)|(?P<STRING>[\'"])|;|}')

    def re_start(self):
        return r'.'

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.span_cssws = self.assign_tokenid(tokenizer, 'default')

        self.span_comment_begin = self.assign_tokenid(tokenizer, 'comment')
        self.span_comment = self.assign_tokenid(tokenizer, 'comment')
        self.span_comment_end = self.assign_tokenid(tokenizer, 'comment')

        self.span_string_begin = self.assign_tokenid(tokenizer, 'string')
        self.span_string = self.assign_tokenid(tokenizer, 'string')
        self.span_string_end = self.assign_tokenid(tokenizer, 'string')

        self.span_selector = self.assign_tokenid(tokenizer, 'css-selector')
        self.span_open_brace = self.assign_tokenid(tokenizer, 'css-selector')
        self.span_close_brace = self.assign_tokenid(tokenizer, 'css-selector')

        self.span_propname = self.assign_tokenid(tokenizer, 'css-propname')
        self.span_colon = self.assign_tokenid(tokenizer, 'css-propname')

        self.span_propvalue = self.assign_tokenid(tokenizer, 'css-propvalue')
        self.span_colon = self.assign_tokenid(tokenizer, 'css-propvalue')
        self.span_semicolon = self.assign_tokenid(tokenizer, 'css-propvalue')
        if self.close:
            self.span_close = self.assign_tokenid(tokenizer, self.closestyle)

    def resume_pos(self, highlighter, tokenizer, doc, pos):
        # Returns top of current keyword
        if 0 < pos < len(doc.styles):
            # resume from top of last selector
            p = doc.styles.rfindint([self.span_selector], 0, pos, comp_ne=False)
            if p == -1:
                return 0
            return p
        return 0

    def on_start(self, tokenizer, doc, pos, match):
        buf = doc.buf
        for f, t, tokenid in self.root_func(buf, match.start()):
            if pos != f:
                assert pos < f
                yield (pos, f, self.span_cssws)
            yield (f, t, tokenid)
            pos = t
            if self.close and tokenid == self.span_close:
                return pos, None, True
        return pos, None, False

    def parse_comment(self, buf, pos):
        m = self.END_COMMENT.search(buf, pos)
        if not m:
            if pos != len(buf):
                yield pos, len(buf), self.span_comment
            return len(buf)

        f, t = m.span()
        if pos != f:
            yield pos, f, self.span_comment

        if m.groupdict().get('CLOSE'):
            yield f, t, self.span_close
            return t

        yield f, t, self.span_comment_end
        return t

    def parse_string(self, buf, pos, qmark):
        reobj = gre.compile(r'(\\.)|({0})'.format(qmark), gre.DOTALL)
        cur = pos
        while True:
            m = reobj.search(buf, cur)
            if not m:
                yield pos, len(buf), self.span_string
                return len(buf)
            if m.group(1):
                cur = m.end()
            else:
                yield pos, m.start(), self.span_string
                yield m.start(), m.end(), self.span_string_end
                return m.end()

    def parse_properties(self, buf, pos):
        while True:
            m = self.PROPERTY_TOP.search(buf, pos)
            if not m:
                if pos != len(buf):
                    yield pos, len(buf), self.span_propname
                return len(buf)

            f, t = m.span()
            if pos != f:
                yield pos, f, self.span_propname

            if m.group('COMMENT'):
                yield f, t, self.span_comment_begin
                pos = yield from self.parse_comment(buf, t)

            elif m.group('STRING'):
                yield f, t, self.span_string_begin
                pos = yield from self.parse_string(buf, t, m.group('STRING'))

            elif m.group() == ':':
                yield f, t, self.span_colon
                pos = yield from self.parse_propvalue(buf, t)

            elif m.groupdict().get('CLOSE'):
                yield f, t, self.span_close
                return t

            else:
                yield f, t, self.span_close_brace
                return t

    root_func = parse_properties

    def parse_propvalue(self, buf, pos):
        while True:
            m = self.PROPERTY_VALUE.search(buf, pos)
            if not m:
                if pos != len(buf):
                    yield pos, len(buf), self.span_propvalue
                return len(buf)

            f, t = m.span()
            if pos != f:
                yield pos, f, self.span_propvalue

            if m.group('COMMENT'):
                yield f, t, self.span_comment_begin
                pos = yield from self.parse_comment(buf, t)

            elif m.group('STRING'):
                yield f, t, self.span_string_begin
                pos = yield from self.parse_string(buf, t, m.group('STRING'))

            elif m.group() == ';':
                yield f, t, self.span_semicolon
                return t

            elif m.groupdict().get('CLOSE'):
                yield f, t, self.span_close
                return t

            else:
                # close brace
                return f


class CSSToken(CSSProp):
    def parse_css(self, buf, pos):
        while True:
            m = self.CSS_TOP.search(buf, pos)
            if not m:
                if pos != len(buf):
                    yield pos, len(buf), self.span_selector
                return len(buf)

            f, t = m.span()
            if pos != f:
                yield pos, f, self.span_selector

            if m.group('COMMENT'):
                yield f, t, self.span_comment_begin
                pos = yield from self.parse_comment(buf, t)

            elif m.group('STRING'):
                yield f, t, self.span_string_begin
                pos = yield from self.parse_string(buf, t, m.group('STRING'))

            elif m.groupdict().get('CLOSE'):
                yield f, t, self.span_close
                return t

            else:
                yield f, t, self.span_open_brace
                pos = yield from self.parse_properties(buf, t)

    root_func = parse_css

def build_tokenizer(close=None, closestyle=None):
    csstoken = CSSToken('css', 'default', close=close, closestyle=closestyle)
    return Tokenizer([csstoken])

def build_proptokenizer(close=None, closestyle=None):
    csstoken = CSSProp('css', 'default', close=close, closestyle=closestyle)
    return Tokenizer([csstoken])


class CSSMode(defaultmode.DefaultMode):
    MODENAME = 'CSS'
    def init_themes(self):
        super().init_themes()
        self.themes.append(CSSThemes)

    def init_tokenizers(self):
        self.tokenizers = [build_tokenizer()]

