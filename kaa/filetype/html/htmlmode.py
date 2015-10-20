import re
from collections import namedtuple
from kaa.filetype.default import defaultmode
from kaa import doc_re
from kaa.highlight import (Tokenizer, Span, SingleToken, Token,
                           SubSection, EndSection, SubTokenizer)
from kaa.theme import Theme, Style
from kaa.filetype.javascript import javascriptmode
from kaa.filetype.css import cssmode

from kaa import encodingdef
from kaa.filetype import filetypedef
from kaa.syntax_highlight import *

def iter_b_attr(b):
    pos = 0
    prop = re.compile(br'(\w+)\s*=\s*', re.DOTALL)
    value = re.compile(b'\s*(("[^"]+")|(\'[^\']+\'))', re.DOTALL)

    while True:
        m = prop.search(b, pos)
        if not m:
            return
        name = m.group(1)
        m = value.match(b, m.end())
        if not m:
            return
        yield name, m.group()[1:-1]
        pos = m.end()


def get_encoding(b):
    # http://www.w3.org/International/questions/qa-html-encoding-declarations

    # HTML5: <meta charset="UTF-8">
    m = re.search(br'<meta ', b, re.DOTALL)
    if m:
        for name, value in iter_b_attr(b[m.end():]):
            if name == b'charset':
                return str(value.strip(), 'utf-8')

    # HTML4, XHTML:
    #    <meta http-equiv="Content-type" content="text/html;charset=UTF-8">
    m = re.search(br'<meta ', b, re.DOTALL)
    if m:
        for name, value in iter_b_attr(b[m.end():]):
            if name == b'content':
                m = re.search(br'charset=(.*)', value, re.DOTALL)
                if m:
                    return str(m.group(1).strip(), 'utf-8')
                break

    # XHTML: <?xml version="1.0" encoding="UTF-8"?>
    m = re.search(br'<\?xml ', b, re.DOTALL)
    if m:
        for name, value in iter_b_attr(b[m.end():]):
            if name == b'encoding':
                return str(value.strip().strip(), 'utf-8')


HTMLThemes = {
    'basic': [
        Style('html-decl', 'Red', 'default'),
        Style('html-tag', 'Magenta', 'default'),
        Style('html-attrname', 'green', 'default'),
        Style('html-attrvalue', 'yellow', 'default'),
    ],
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

        yield f, f + 1, self.span_attrvalue
        js_to, tok, close = yield from func.iter_subtokenizers(None, doc, f + 1, None)

        pos = js_to
        if js_to < doc.endpos():
            yield js_to, js_to + 1, self.span_attrvalue
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

        yield f, f + 1, self.span_attrvalue
        pos, tok, close = yield from func.iter_subtokenizers(None, doc, f + 1, None)
        return pos

    RE_ELEMNAME = doc_re.compile(r'\s*[^>\s]+')
    RE_CLOSE = doc_re.compile(r'\s*/?>', doc_re.S)

    RE_ATTRNAME = doc_re.compile(
        r'>|(?P<ATTRNAME>[-._:a-zA-Z0-9]+)(?P<EQUAL>\s*=)?\s*')
    RE_ATTRVALUE = doc_re.compile(r'\s*(?P<ATTRVALUE>({}))'.format(
        '|'.join(['[-._:a-zA-Z0-9]+', '(?P<Q1>"[^"]*")', "(?P<Q2>'[^']*')"])))

    def iter_attrs(self, tokenizer, doc, pos, attrs):
        while True:
            m = self.RE_ATTRNAME.search(doc, pos)
            if not m:
                return pos
            if m.group() == '>':
                return m.start()

            # yield attribute name
            f, t = m.span('ATTRNAME')
            yield f, t, self.span_attrname
            attrname = m.group('ATTRNAME')

            # save attr-name
            attrs.append([attrname, None])

            # yield after attr-name
            pos = m.end()

            # has attribute value?
            if m.group('EQUAL'):
                # yield values after '='
                m = self.RE_ATTRVALUE.match(doc, pos)
                if m:
                    attrvalue = m.group('ATTRVALUE')

                    # save attr-name
                    if m.group('Q1') or m.group('Q2'):
                        attrvalue = attrvalue[1:-1]
                    attrs[-1][1] = attrvalue

                    if attrname.lower().startswith('on'):
                        pos = yield from self.yield_jsattr(tokenizer, doc, m)
                    elif attrname.lower() == 'style':
                        pos = yield from self.yield_cssattr(tokenizer, doc, m)
                    else:
                        f, t = m.span('ATTRVALUE')
                        yield f, t, self.span_attrvalue
                        pos = t

    def iter_tokens(self, tokenizer, doc, pos, attrs):
        match = self.RE_ELEMNAME.match(doc, pos)
        if not match:
            return
        yield (pos, match.end(), self.span_elemname)

        pos = match.end()
        pos = yield from self.iter_attrs(tokenizer, doc, pos, attrs)

        m = self.RE_CLOSE.match(doc, pos)
        if m:
            yield pos, m.end(), self.span_gt

    def get_contents_tokenizer(self, tokenizer, doc, pos, attrs):
        return pos, None, False

    def iter_tag(self, tokenizer, doc, pos, f):
        yield (f, f + 1, self.span_lt)

        pos = f + 1
        attrs = []
        for f, t, tokenid in self.iter_tokens(tokenizer, doc, pos, attrs):
            assert f <= t
            assert pos <= f
            if pos != f:
                yield (pos, f, self.span_elemws)
            yield (f, t, tokenid)
            pos = t

        pos, childtokenizer, close = self.get_contents_tokenizer(
            tokenizer, doc, pos, attrs)
        return pos, childtokenizer, close

    def on_start(self, tokenizer, doc, pos, match):
        ret = yield from self.iter_tag(tokenizer, doc, pos, match.start())
        return ret


class ScriptTag(HTMLTag):

    def __init__(self, name, stylename, jstokenizer):
        super().__init__(name, stylename)
        self.jstokenizer = jstokenizer

    def re_start(self):
        return r'<\s*script'

    def get_contents_tokenizer(self, tokenizer, doc, pos, attrs):
        for name, value in attrs:
            if name == 'type':
                if value and value.lower() != 'text/javascript':
                    return pos, None, False
                break

        return pos, self.jstokenizer, False


def build_tokenizers():

    HTMLTOKENS = namedtuple('htmltokens',
                            ['keywords', 'comment', 'xmlpi', 'xmldef', 'jsstop', 'endtag',
                             'scripttag', 'cssstart', 'htmltag', 'jsattr1', 'jsattr2',
                             'cssattr1', 'cssattr2'])

    keywords = SingleToken('html-entityrefs', 'keyword',
                           [r'&\w+;', r'&\#x[0-9a-hA-H]+;', r'&\#[0-9]+;'])

    comment = Span('html-comment', 'comment', r'<!--', r'--\s*>')
    xmlpi = Span('xmlpi', 'html-decl', r'<\?', r'\?>')
    xmldef = Span('xmldef', 'html-decl', r'<!', r'>')

    jsstop = SingleToken('end-javascript', 'html-tag', [r'</\s*script\s*>'])
    jstokenizer = javascriptmode.build_tokenizer(terminates=r'</\s*script\s*>')

    scripttag = ScriptTag('script', 'default', jstokenizer)

    endtag = Span('html-endtag', 'html-tag', r'</', r'>')
    htmltag = HTMLTag('html', 'default')

    csstokenizer = cssmode.build_tokenizer(r'</\s*style\s*>', 'html-tag')

    cssstart = SubSection('start-css', 'html-tag',
                          r'<\s*style(\s+[^>]*)*>', csstokenizer)

    jsattr1 = SubTokenizer(
        'sub-js', '', javascriptmode.build_tokenizer(terminates="'"))
    jsattr2 = SubTokenizer(
        'sub-js', '', javascriptmode.build_tokenizer(terminates='"'))

    styleattr1 = SubTokenizer(
        'sub-css', '', cssmode.build_proptokenizer("'", 'html-attrvalue'))
    styleattr2 = SubTokenizer(
        'sub-css', '', cssmode.build_proptokenizer('"', 'html-attrvalue'))

    return [Tokenizer(
        HTMLTOKENS(
            keywords, comment, xmlpi, xmldef, jsstop, endtag, scripttag, cssstart, htmltag,
            jsattr1, jsattr2, styleattr1, styleattr2)),
            jstokenizer, csstokenizer]


RE_ATTRNAME = doc_re.compile(
    r'>|(?P<ATTRNAME>[-._:a-zA-Z0-9]+)(?P<EQUAL>\s*=)?\s*')
RE_ATTRVALUE = doc_re.compile(r'\s*(?P<ATTRVALUE>({}))'.format(
    '|'.join(['[-._:a-zA-Z0-9]+', '(?P<Q1>"[^"]*")', "(?P<Q2>'[^']*')"])))

def iter_attrs(doc, pos):
    while True:
        m = RE_ATTRNAME.search(doc, pos)
        if not m:
            return pos
        if m.group() == '>':
            return m.start()

        attrname = m.group('ATTRNAME')
        pos = m.end()

        # has attribute value?
        if m.group('EQUAL'):
            # yield values after '='
            m = RE_ATTRVALUE.match(doc, pos)
            if m:
                pos = m.end()
                attrvalue = m.group('ATTRVALUE')
                if m.group('Q1') or m.group('Q2'):
                    attrvalue = attrvalue[1:-1]
                    yield attrname, attrvalue
                    continue

        yield attrname, None
                
class HTMLTag(SingleToken):
    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if match.group('closetag'):
            return pos, terminates

        if pos < doc.endpos():
            pos = yield from self.tokenizer.AttrTokenizer.run(doc, pos)
            if pos < doc.endpos():
                c = doc.gettext(pos, pos+1)
                if c == '>':
                    yield (pos, pos+1, self.styleid_token)
                    pos += 1
        return pos, terminates
    

class HTMLScriptTag(HTMLTag):
    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if match.group('closetag'):
            return pos, terminates

        for name, value in iter_attrs(doc, match.start()):
            if name.lower() == 'type':
                if value and value.lower() != 'text/javascript':
                    return pos, terminates

        pos = yield from self.tokenizer.JSTokenizer.run(doc, pos)
        return pos, terminates
        
class HTMLStyleTag(HTMLTag):
    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if match.group('closetag'):
            return pos, terminates

        pos = yield from self.tokenizer.CSSTokenizer.run(doc, pos)

        return pos, terminates
        
class HTMLAttr(SingleToken):
    def prepare(self):
        super().prepare()

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if not terminates and match.group(0)[-1].strip().endswith("="):
            if pos >= doc.endpos():
                return pos, terminates

            c = doc.gettext(pos, pos+1)
            attrname = match.group('attrname')
            attrname = attrname.lower() if attrname else ''

            if attrname.startswith('on'):
                if c == "'":
                    yield (pos, pos+1, self.styleid_token)
                    pos = yield from self.tokenizer.AttrValueJSTokenizer1.run(doc, pos+1)
                elif c == '"':
                    yield (pos, pos+1, self.styleid_token)
                    pos = yield from self.tokenizer.AttrValueJSTokenizer2.run(doc, pos+1)
            elif attrname == 'style':
                if c == "'":
                    yield (pos, pos+1, self.styleid_token)
                    pos = yield from self.tokenizer.AttrValueCSSTokenizer1.run(doc, pos+1)
                elif c == '"':
                    yield (pos, pos+1, self.styleid_token)
                    pos = yield from self.tokenizer.AttrValueCSSTokenizer2.run(doc, pos+1)
            else:
                if c == "'":
                    yield (pos, pos+1, self.styleid_token)
                    pos = yield from self.tokenizer.AttrValueTokenizer1.run(doc, pos+1)
                elif c == '"':
                    yield (pos, pos+1, self.styleid_token)
                    pos = yield from self.tokenizer.AttrValueTokenizer2.run(doc, pos+1)
                else:
                    pos = yield from self.tokenizer.AttrValueTokenizer3.run(doc, pos)

        return pos, terminates


def make_tokenizer():
    ret = Tokenizer(tokens=[
        ('html-entityrefs', SingleToken('keyword',
                           [r'&\w+;', r'&\#x[0-9a-hA-H]+;', r'&\#[0-9]+;'])),
        ('comment', Span('comment', r'<!--', r'--\s*>')),
        ('xmlpi', Span('html-decl', r'<\?', r'\?>')),
        ('xmldef', Span('html-decl', r'<!', r'>')),
        ('styletag', HTMLStyleTag('html-tag', [r'<\s*style'])),
        ('scripttag', HTMLScriptTag('html-tag', [r'<\s*script'])),
        ('tag', HTMLTag('html-tag', [r'<(?P<closetag>/)?\s*\S+'])),
    ])


    ret.AttrTokenizer = Tokenizer(parent=ret, terminates='>', 
        is_resumable=False, tokens=[
            ('attr', HTMLAttr('html-attrname', [r'(?P<attrname>[^\s=>]+)\s*=?\s*'])),
    ])

    ret.AttrTokenizer.AttrValueTokenizer1 = Tokenizer(parent=ret.AttrTokenizer,
        tokens=[('value', SingleToken('html-attrvalue', [r"[^']*'"], terminates=True))])

    ret.AttrTokenizer.AttrValueTokenizer2 = Tokenizer(parent=ret.AttrTokenizer, 
        tokens=[('value', SingleToken('html-attrvalue', [r'[^"]*"'], terminates=True))])

    ret.AttrTokenizer.AttrValueTokenizer3 = Tokenizer(parent=ret.AttrTokenizer, 
        tokens=[('value', SingleToken('html-attrvalue', [r'\w*'], terminates=True))])

    ret.AttrTokenizer.AttrValueJSTokenizer1 = Tokenizer(parent=ret.AttrTokenizer,
        tokens=javascriptmode.javascript_tokens(), terminates="'")

    ret.AttrTokenizer.AttrValueJSTokenizer2 = Tokenizer(parent=ret.AttrTokenizer,
        tokens=javascriptmode.javascript_tokens(), terminates='"')

    ret.AttrTokenizer.AttrValueCSSTokenizer1 = cssmode.make_prop_tokenizer(ret.AttrTokenizer, "'")
    ret.AttrTokenizer.AttrValueCSSTokenizer2 = cssmode.make_prop_tokenizer(ret.AttrTokenizer, '"')


    ret.JSTokenizer = Tokenizer(parent=ret, 
        tokens=javascriptmode.javascript_tokens(), terminates=r"</.*script[^>]*>")

    ret.CSSTokenizer = cssmode.make_tokenizer(ret, terminates=r"</.*style[^>]*>")

    return ret



class HTMLMode(defaultmode.DefaultMode):
    MODENAME = 'HTML'

    tokenizer = make_tokenizer()

    @classmethod
    def update_fileinfo(cls, fileinfo, document=None):
        try:
            buffer = open(fileinfo.fullpathname, 'rb').read(1024)
            enc = get_encoding(buffer)
            if enc:
                enc = encodingdef.normalize_encname(enc,
                                                    fileinfo.encoding)
                fileinfo.encoding = enc
        except IOError:
            pass

    def init_themes(self):
        super().init_themes()
        self.themes.append(HTMLThemes)
        self.themes.append(cssmode.CSSThemes)
        self.themes.append(javascriptmode.JavaScriptThemes)
