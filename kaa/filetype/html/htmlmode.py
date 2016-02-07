import re
from kaa.filetype.default import defaultmode
from kaa import doc_re
from kaa.theme import Style
from kaa.filetype.javascript import javascriptmode
from kaa.filetype.css import cssmode

from kaa import encodingdef
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
        if pos < doc.endpos():
            pos = yield from self.tokenizer.AttrTokenizer.run(doc, pos)
            if pos < doc.endpos():
                c = doc.gettext(pos, pos + 1)
                if c == '>':
                    yield (pos, pos + 1, self.styleid_token)
                    pos += 1
        return pos, terminates


class HTMLScriptTag(HTMLTag):

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)

        for name, value in iter_attrs(doc, match.start()):
            if name.lower() == 'type':
                if value and value.lower() != 'text/javascript':
                    return pos, terminates

        pos = yield from self.tokenizer.JSTokenizer.run(doc, pos)
        return pos, terminates


class HTMLStyleTag(HTMLTag):

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)

        pos = yield from self.tokenizer.CSSTokenizer.run(doc, pos)

        return pos, terminates


class HTMLAttr(SingleToken):

    def __init__(self, stylename, value_stylename, tokens, terminates=False):
        super().__init__(stylename, tokens, terminates=terminates)
        self._value_stylename = value_stylename

    def prepare(self):
        super().prepare()
        self.register_styles([(self._value_stylename, "styleid_value")])

    def on_start(self, doc, match):
        pos, terminates = yield from super().on_start(doc, match)
        if not terminates and match.group(0)[-1].strip().endswith("="):
            if pos >= doc.endpos():
                return pos, terminates

            c = doc.gettext(pos, pos + 1)
            attrname = match.group('attrname')
            attrname = attrname.lower() if attrname else ''

            if c in {"'", '"'}:
                yield (pos, pos + 1, self.styleid_value)

            if attrname.startswith('on'):
                if c == "'":
                    pos = yield from self.tokenizer.AttrValueJSTokenizer1.run(doc, pos + 1)
                elif c == '"':
                    pos = yield from self.tokenizer.AttrValueJSTokenizer2.run(doc, pos + 1)

                if pos < doc.endpos():
                    if doc.gettext(pos, pos + 1) == c:
                        yield (pos, pos + 1, self.styleid_value)
                        pos += 1

            elif attrname == 'style':
                if c == "'":
                    pos = yield from self.tokenizer.AttrValueCSSTokenizer1.run(doc, pos + 1)
                elif c == '"':
                    pos = yield from self.tokenizer.AttrValueCSSTokenizer2.run(doc, pos + 1)

                if pos < doc.endpos():
                    if doc.gettext(pos, pos + 1) == c:
                        yield (pos, pos + 1, self.styleid_value)
                        pos += 1
            else:
                if c == "'":
                    pos = yield from self.tokenizer.AttrValueTokenizer1.run(doc, pos + 1)
                elif c == '"':
                    pos = yield from self.tokenizer.AttrValueTokenizer2.run(doc, pos + 1)
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
        ('closetag', SingleToken('html-tag', [r'</\s*[^>]+>'])),
        ('tag', HTMLTag('html-tag', [r'<\s*[^>\s]*'])),
    ])

    ret.AttrTokenizer = Tokenizer(parent=ret, terminates='>',
                                  is_resumable=False, tokens=[
                                      ('attr', HTMLAttr('html-attrname', 'html-attrvalue',
                                                        [r'(?P<attrname>[^\s=>]+)\s*=?\s*'])),
                                  ])

    ret.AttrTokenizer.AttrValueTokenizer1 = Tokenizer(
        parent=ret.AttrTokenizer,
        tokens=[('value', SingleToken('html-attrvalue', [r"[^']*'"], terminates=True))])

    ret.AttrTokenizer.AttrValueTokenizer2 = Tokenizer(
        parent=ret.AttrTokenizer,
        tokens=[('value', SingleToken('html-attrvalue', [r'[^"]*"'], terminates=True))])

    ret.AttrTokenizer.AttrValueTokenizer3 = Tokenizer(
        parent=ret.AttrTokenizer,
        tokens=[('value', SingleToken('html-attrvalue', [r'\w*'], terminates=True))])

    ret.AttrTokenizer.AttrValueJSTokenizer1 = Tokenizer(
        parent=ret.AttrTokenizer,
        tokens=javascriptmode.javascript_tokens(), terminates="'")

    ret.AttrTokenizer.AttrValueJSTokenizer2 = Tokenizer(
        parent=ret.AttrTokenizer,
        tokens=javascriptmode.javascript_tokens(), terminates='"')

    ret.AttrTokenizer.AttrValueCSSTokenizer1 = cssmode.make_prop_tokenizer(
        ret.AttrTokenizer, "'")
    ret.AttrTokenizer.AttrValueCSSTokenizer2 = cssmode.make_prop_tokenizer(
        ret.AttrTokenizer, '"')

    ret.JSTokenizer = Tokenizer(parent=ret,
                                tokens=javascriptmode.javascript_tokens(), terminates=r"</.*script[^>]*>")

    ret.CSSTokenizer = cssmode.make_tokenizer(
        ret, terminates=r"</.*style[^>]*>")

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
