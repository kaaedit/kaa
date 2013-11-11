from collections import namedtuple
from kaa.filetype.default import defaultmode
from gappedbuf import re as gre
from kaa.highlight import (Tokenizer, Span, SingleToken, Token, 
        SubSection, EndSection, SubTokenizer)
from kaa.theme import Theme, Style
from kaa.filetype.javascript import javascriptmode
from kaa.filetype.css import cssmode

HTMLThemes = {
    'basic':
        Theme([
            Style('html-decl', 'Red', 'default'),
            Style('html-tag', 'Magenta', 'default'),
            Style('html-attrname', 'green', 'default'),
            Style('html-attrvalue', 'yellow', 'default'),
        ]),
}

class HTMLTag(Token):
    def re_start(self):
        return r'<'

    def prepare(self, tokenizer):
        super().prepare(tokenizer)

        self.span_lt = self.assign_tokenid(tokenizer, 'html-tag')
        self.span_gt = self.assign_tokenid(tokenizer, 'html-tag')
        self.span_elemname = self.assign_tokenid(tokenizer, 'html-tag')
        self.span_attrname = self.assign_tokenid(tokenizer, 'html-attrname')
        self.span_attrvalue = self.assign_tokenid(tokenizer, 'html-attrvalue')
        self.span_elemws = self.assign_tokenid(tokenizer, 'default')

    def resume_pos(self, highlighter, tokenizer, doc, pos):
        # Returns top of current keyword
        if 0 < pos < len(doc.styles):
            p = doc.styles.rfindint([self.span_lt],
                0, pos, comp_ne=False)
            if p != -1:
                return p
        return 0

    def yield_jsattr(self, tokenizer, doc, match):
        f, t = match.span('ATTRVALUE')
        if match.group('Q1'):
            func = tokenizer.tokens.jsattr2
        elif match.group('Q2'):
            func = tokenizer.tokens.jsattr1
        else:
            # no quotation mark. ignore this value.
            yield match.start(), match.end(), self.span_attrvalue
            return match.end()

        yield f, f+1, self.span_attrvalue
        js_to, tok, close = yield from func.iter_subtokenizers(None, doc, f+1, None)

        pos = js_to
        if js_to < doc.endpos():
            yield js_to, js_to+1, self.span_attrvalue
            pos = js_to + 1

        return pos

    def yield_cssattr(self, tokenizer, doc, match):
        f, t = match.span('ATTRVALUE')
        if match.group('Q1'):
            func = tokenizer.tokens.cssattr2
        elif match.group('Q2'):
            func = tokenizer.tokens.cssattr1
        else:
            # no quotation mark. ignore this value.
            yield match.start(), match.end(), self.span_attrvalue
            return match.end()

        yield f, f+1, self.span_attrvalue
        pos, tok, close = yield from func.iter_subtokenizers(None, doc, f+1, None)
        return pos

    RE_ELEMNAME=gre.compile(r'\s*[^>\s]+')
    RE_CLOSE=gre.compile(r'\s*/?>', gre.S)

    RE_ATTRNAME=gre.compile(r'>|(?P<ATTRNAME>[-._:a-zA-Z0-9]+)(?P<EQUAL>\s*=)?\s*')
    RE_ATTRVALUE=gre.compile(r'\s*(?P<ATTRVALUE>({}))'.format(
        '|'.join(['[-._:a-zA-Z0-9]+', '(?P<Q1>"[^"]*")', "(?P<Q2>'[^']*')"])))

    def iter_attrs(self, tokenizer, doc, pos):
        buf = doc.buf
        while True:
            m = self.RE_ATTRNAME.search(buf, pos)
            if not m:
                return pos
            if m.group() == '>':
                return pos

            # yield attribute name
            f, t = m.span('ATTRNAME')
            yield f, t, self.span_attrname
            attrname = m.group('ATTRNAME')

            # yield after attr-name
            pos = m.end()
            if t != pos:
                yield t, pos, self.span_elemws

            # has attribute value?
            if m.group('EQUAL'):
                # yield values after '='
                m = self.RE_ATTRVALUE.match(buf, pos)
                if m:
                    attrvalue = m.group('ATTRVALUE')
                    f, t = m.span('ATTRVALUE')

                    if attrname.lower().startswith('on'):
                        pos = yield from self.yield_jsattr(tokenizer, doc, m)
                    elif attrname.lower() == 'style':
                        pos = yield from self.yield_cssattr(tokenizer, doc, m)
                    else:
                        yield f, t, self.span_attrvalue
                        pos = t

    def iter_tokens(self, tokenizer, doc, pos):
        buf = doc.buf
        match = self.RE_ELEMNAME.match(buf, pos)
        if not match:
            yield pos, len(buf), self.span_elemws
            return
        yield (pos, match.end(), self.span_elemname)

        pos = match.end()
        pos = yield from self.iter_attrs(tokenizer, doc, pos)

        m = self.RE_CLOSE.match(buf, pos)
        if m:
            yield pos, m.end(), self.span_gt
            return m.end()
        else:
            if pos != len(buf):
                yield pos, len(buf), self.span_elemws
            return len(buf)

    def on_start(self, tokenizer, doc, pos, match):
        buf = doc.buf

        yield (match.start(), match.end(), self.span_lt)

        pos = match.end()
        for f, t, tokenid in self.iter_tokens(tokenizer, doc, match.end()):
            assert f < t
            assert pos <= f
            if pos != f:
                yield (pos, f, self.span_elemws)
            yield (f, t, tokenid)
            pos = t
        return pos, None, False


def build_tokenizers():

    HTMLTOKENS = namedtuple('htmltokens', ['keywords', 'comment',
                       'xmlpi', 'xmldef', 'endtag', 'jsstart', 'cssstart',
                       'htmltag', 'jsattr1', 'jsattr2', 'cssattr1',
                       'cssattr2'])

    keywords=SingleToken('html-entityrefs', 'keyword',
                         [r'&\w+;', r'&\#x[0-9a-hA-H]+;', r'&\#[0-9]+;'])

    comment=Span('html-comment', 'comment', r'<!--', r'--\s*>')
    xmlpi=Span('xmlpi', 'html-decl', r'<\?', r'\?>')
    xmldef=Span('xmldef', 'html-decl', r'<!', r'>')

    endtag = Span('html-endtag', 'html-tag', r'</', r'>')
    htmltag = HTMLTag('html', 'default')


    jsstop = EndSection('end-javascript', 'html-tag', r'</\s*script\s*>')
    jstokenizer = javascriptmode.build_tokenizer(jsstop)

    jsstart = SubSection('start-javascript', 'html-tag',
                         r'<\s*script(\s+[^>]*)*>', jstokenizer)

    csstokenizer = cssmode.build_tokenizer(r'</\s*style\s*>', 'html-tag')

    cssstart = SubSection('start-css', 'html-tag',
                         r'<\s*style(\s+[^>]*)*>', csstokenizer)

    jsattr1 = SubTokenizer('sub-js', '', javascriptmode.build_tokenizer(terminates="'"))
    jsattr2 = SubTokenizer('sub-js', '', javascriptmode.build_tokenizer(terminates='"'))

    styleattr1 = SubTokenizer('sub-css', '', cssmode.build_proptokenizer("'", 'html-attrvalue'))
    styleattr2 = SubTokenizer('sub-css', '', cssmode.build_proptokenizer('"', 'html-attrvalue'))

    return [Tokenizer(
        HTMLTOKENS(keywords, comment, xmlpi, xmldef, endtag, jsstart, cssstart, htmltag,
                   jsattr1, jsattr2, styleattr1, styleattr2)),
        jstokenizer, csstokenizer]


class HTMLMode(defaultmode.DefaultMode):
    MODENAME = 'HTML'
    def init_themes(self):
        super().init_themes()
        self.themes.append(HTMLThemes)
        self.themes.append(cssmode.CSSThemes)
        self.themes.append(javascriptmode.JavaScriptThemes)

    def init_tokenizers(self):
        self.tokenizers = build_tokenizers()

