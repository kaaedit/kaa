import kaa_testutils
from kaa.filetype.html import htmlmode
from kaa.filetype.html.htmlmode import get_encoding


class TestHTMLHighlight(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = htmlmode.HTMLMode
    TOKENIZER = htmlmode.HTMLMode.tokenizer
    AttrTokenizer = TOKENIZER.AttrTokenizer

    ValueTokenizer1 = TOKENIZER.AttrTokenizer.AttrValueTokenizer1
    ValueTokenizer2 = TOKENIZER.AttrTokenizer.AttrValueTokenizer2
    ValueTokenizer3 = TOKENIZER.AttrTokenizer.AttrValueTokenizer3

    def test_highlight(self):
        doc = self._getdoc('<a b=c d="e" f=\'g\'>')
        doc.mode.run_tokenizer(None)
        
        kaa_testutils.check_style(doc, 0, 19, 
            [self.TOKENIZER.tokens.tag] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 + 
            [self.AttrTokenizer.tokens.attr] * 2 +
            [self.ValueTokenizer3.tokens.value] * 1 +
            [self.AttrTokenizer.tokens.default] * 1 +
            [self.AttrTokenizer.tokens.attr] * 3 +
            [self.ValueTokenizer2.tokens.value] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 +
            [self.AttrTokenizer.tokens.attr] * 3 +
            [self.ValueTokenizer1.tokens.value] * 2 +
            [self.TOKENIZER.tokens.tag] * 1)

    ValueJSTokenizer1 = TOKENIZER.AttrTokenizer.AttrValueJSTokenizer1
    ValueJSTokenizer2 = TOKENIZER.AttrTokenizer.AttrValueJSTokenizer2

    def test_jsattr(self):
        doc = self._getdoc("<a ona='if'>")
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 12, 
            [self.TOKENIZER.tokens.tag] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 + 
            [self.AttrTokenizer.tokens.attr] * 5 +
            [self.ValueJSTokenizer1.tokens.keyword] * 2 +
            [self.AttrTokenizer.tokens.attr] * 1 +
            [self.TOKENIZER.tokens.tag] * 1)

        doc = self._getdoc('<a ona="if">')
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 12, 
            [self.TOKENIZER.tokens.tag] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 + 
            [self.AttrTokenizer.tokens.attr] * 5 +
            [self.ValueJSTokenizer2.tokens.keyword] * 2 +
            [self.AttrTokenizer.tokens.attr] * 1 +
            [self.TOKENIZER.tokens.tag] * 1)

    JSTokenizer = TOKENIZER.JSTokenizer
    def test_jselem(self):
        doc = self._getdoc("<script>if</script>")

        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 19, 
            [self.TOKENIZER.tokens.scripttag] * 8 +
            [self.JSTokenizer.tokens.keyword] * 2 +
            [self.TOKENIZER.tokens.closetag] * 9)


    AttrCSSTokenizer1 = TOKENIZER.AttrTokenizer.AttrValueCSSTokenizer1
    PropValueTokenizer1 = AttrCSSTokenizer1.PropValueTokenizer

    AttrCSSTokenizer2 = TOKENIZER.AttrTokenizer.AttrValueCSSTokenizer2
    PropValueTokenizer2 = AttrCSSTokenizer2.PropValueTokenizer

    def test_cssattr(self):
        doc = self._getdoc("<a style='a:b'>")
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 15, 
            [self.TOKENIZER.tokens.tag] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 + 
            [self.AttrTokenizer.tokens.attr] * 7 +
            [self.AttrCSSTokenizer1.tokens.propname] * 2 +
            [self.PropValueTokenizer1.tokens.string] * 1 +
            [self.AttrTokenizer.tokens.attr] * 1 +
            [self.TOKENIZER.tokens.tag] * 1)


        doc = self._getdoc('<a style="a:b">')
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 15, 
            [self.TOKENIZER.tokens.tag] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 + 
            [self.AttrTokenizer.tokens.attr] * 7 +
            [self.AttrCSSTokenizer2.tokens.propname] * 2 +
            [self.PropValueTokenizer2.tokens.string] * 1 +
            [self.AttrTokenizer.tokens.attr] * 1 +
            [self.TOKENIZER.tokens.tag] * 1)

        kaa_testutils.check_style(doc, 0, 15, 
            [self.TOKENIZER.tokens.tag] * 2 +
            [self.AttrTokenizer.tokens.default] * 1 + 
            [self.AttrTokenizer.tokens.attr] * 7 +
            [self.AttrCSSTokenizer2.tokens.propname] * 2 +
            [self.PropValueTokenizer2.tokens.string] * 1 +
            [self.AttrTokenizer.tokens.attr] * 1 +
            [self.TOKENIZER.tokens.tag] * 1)

    CSSTokenizer = TOKENIZER.CSSTokenizer
    CSSPropTokenizer = CSSTokenizer.PropTokenizer
    CSSPropValueTokenizer = CSSPropTokenizer.PropValueTokenizer
    def test_csselem(self):
        doc = self._getdoc("<style>a{b:c}</style>")
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 21, 
            [self.TOKENIZER.tokens.styletag] * 7 +
            [self.CSSTokenizer.tokens.default] * 1 +
            [self.CSSTokenizer.tokens.ruleset] * 1 +
            [self.CSSPropTokenizer.tokens.propname] * 2	 +
            [self.CSSPropValueTokenizer.tokens.string] * 1 +
            [self.CSSPropTokenizer.tokens.terminate_name] * 1 +
            [self.TOKENIZER.tokens.closetag] * 8 )


class TestEncDecl:

    def test_html5(self):
        assert 'UTF-8' == get_encoding(b'<meta charset="UTF-8">')
        assert 'UTF-8' == get_encoding(b"<meta charset='UTF-8'>")
        assert not get_encoding(b"<meta charset='UTF-8>")

    def test_html(self):
        assert 'UTF-8' == get_encoding(
            b'''<meta http-equiv="Content-type"
            content="text/html;charset=UTF-8">''')

        assert not get_encoding(
            b'''<meta con="text/html;charset=UTF-8">''')

        assert not get_encoding(
            b'''<meta content="text/html;char=UTF-8">''')

    def test_xml(self):
        assert 'UTF-8' == get_encoding(
            b'<?xml version="1.0" encoding="UTF-8"?>')

        assert not get_encoding(
            b'<?xm version="1.0" encoding="UTF-8"?>')

        assert not get_encoding(
            b'<?xml version="1.0" encoding=""?>')
