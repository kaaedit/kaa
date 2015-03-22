import kaa_testutils
from kaa import highlight
from kaa.filetype.html import htmlmode
from kaa.filetype.html.htmlmode import get_encoding

class TestHTMLHighlight(kaa_testutils._TestDocBase):
    tokenizers = htmlmode.build_tokenizers()

    def test_entity(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('&lt; &#1111; &#x2222;')

        assert [
            (0, 4, self.tokenizers[0].tokens.keywords.tokenid),
            (4, 5, hl.tokenizers[0].nulltoken),
            (5, 12, self.tokenizers[0].tokens.keywords.tokenid),
            (12, 13, hl.tokenizers[0].nulltoken),
            (13, 21, self.tokenizers[0].tokens.keywords.tokenid)
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_comment(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('<!--abc-->')

        assert [
            (0, 4, self.tokenizers[0].tokens.comment.span_start),
            (4, 7, self.tokenizers[0].tokens.comment.span_mid),
            (7, 10, self.tokenizers[0].tokens.comment.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('<!--abc-x->')

        assert [
            (0, 4, self.tokenizers[0].tokens.comment.span_start),
            (4, 11, self.tokenizers[0].tokens.comment.span_mid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_endtag(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('</abc>')

        assert [
            (0, 2, self.tokenizers[0].tokens.endtag.span_start),
            (2, 5, self.tokenizers[0].tokens.endtag.span_mid),
            (5, 6, self.tokenizers[0].tokens.endtag.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_elem(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('<a> ')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_gt),
            (3, 4, hl.tokenizers[0].nulltoken),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('< abc > ')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 5, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (5, 6, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_gt),
            (7, 8, hl.tokenizers[0].nulltoken),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('<abc xyz>')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 5, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (5, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 9, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('<abc xyz = opq>')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 5, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (5, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 11, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (11, 14, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (14, 15, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('<abc xyz = "opq">')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 5, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (5, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 11, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (11, 16, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (16, 17, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc("<abc xyz = 'opq' abc=123>")
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 5, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (5, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 11, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (11, 16, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (16, 17, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (17, 20, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (20, 21, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (21, 24, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (24, 25, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc("<abc xyz= ")
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 5, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (5, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 10, hl.tokenizers[0].tokens.htmltag.span_elemws),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc("<abc xyz=>")
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 5, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (5, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 9, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (9, 10, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc("<abc =>")
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 4, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (4, 6, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_javascript(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc("&nbsp;<script>if</script>if&nbsp;")
        assert [
            (0, 6, hl.tokenizers[0].tokens.keywords.tokenid),
            (6, 14, hl.tokenizers[0].tokens.jsstart.section_start),
            (14, 16, hl.tokenizers[1].tokens.keywords.tokenid),
            (16, 25, hl.tokenizers[1].tokens.stop.section_end),
            (25, 27, hl.tokenizers[0].nulltoken),
            (27, 33, hl.tokenizers[0].tokens.keywords.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc("&nbsp;<script>/abc/</script>if&nbsp;")
        hl.update_style(doc)
        assert ([hl.tokenizers[0].tokens.keywords.tokenid]*6 +
                [hl.tokenizers[0].tokens.jsstart.section_start]*8 +
                [hl.tokenizers[1].tokens.regex.span_start] +
                [hl.tokenizers[1].tokens.regex.span_mid]*3 +
                [hl.tokenizers[1].tokens.regex.span_end] +
                [hl.tokenizers[1].tokens.stop.section_end]*9 +
                [hl.tokenizers[0].nulltoken]*2 +
                [hl.tokenizers[0].tokens.keywords.tokenid]*6
               ) == doc.styles.getints(0, 36)

    def test_style(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc("<style>a</style>&nbsp;")
        assert [
            (0, 7, hl.tokenizers[0].tokens.cssstart.section_start),
            (7, 8, hl.tokenizers[2].tokens[0].span_selector),
            (8, 16, hl.tokenizers[2].tokens[-1].span_close),
            (16, 22, hl.tokenizers[0].tokens.keywords.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_javascriptattr1(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc("<a ona='if'>")
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (3, 6, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (7, 8, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (8, 10, hl.tokenizers[0]
             .tokens.jsattr1.subtokenizer.tokens.keywords.tokenid),
            (10, 11, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (11, 12, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_javascriptattr2(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('<a ona="if">')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (3, 6, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (7, 8, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (8, 10, hl.tokenizers[0]
             .tokens.jsattr2.subtokenizer.tokens.keywords.tokenid),
            (10, 11, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (11, 12, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_javascriptattr3(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('<a ona="if>')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (3, 6, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (7, 8, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (8, 10, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (10, 11, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_javascriptattr4(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('''<a ona='//\n\'''')

        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (3, 6, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (7, 8, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (8, 10, hl.tokenizers[0].
                     tokens.jsattr1.subtokenizer.tokens.comment2.span_start),
            (10, 11, hl.tokenizers[0].tokens.jsattr1.subtokenizer.nulltoken),
            (11, 12, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_javascriptattr5(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('''<a ona='/a/\'''')
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (3, 6, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (6, 7, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (7, 8, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (8, 9, hl.tokenizers[0].
                     tokens.jsattr1.subtokenizer.tokens.regex.span_start),
            (9, 10, hl.tokenizers[0].
                     tokens.jsattr1.subtokenizer.tokens.regex.span_mid),
            (10, 11, hl.tokenizers[0].
                     tokens.jsattr1.subtokenizer.tokens.regex.span_end),
            (11, 12, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_cssattr(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc("<a style=''>")
        assert [
            (0, 1, hl.tokenizers[0].tokens.htmltag.span_lt),
            (1, 2, hl.tokenizers[0].tokens.htmltag.span_elemname),
            (2, 3, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (3, 8, hl.tokenizers[0].tokens.htmltag.span_attrname),
            (8, 9, hl.tokenizers[0].tokens.htmltag.span_elemws),
            (9, 10, hl.tokenizers[0].tokens.htmltag.span_attrvalue),
            (10, 11, hl.tokenizers[0]
             .tokens.cssattr1.subtokenizer.tokens[0].span_close),
            (11, 12, hl.tokenizers[0].tokens.htmltag.span_gt),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_xhtml(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc("""<?xml version="1.0" encoding="utf-8" ?>""")
        assert [
            (0, 2, self.tokenizers[0].tokens.xmlpi.span_start),
            (2, 37, self.tokenizers[0].tokens.xmlpi.span_mid),
            (37, 39, self.tokenizers[0].tokens.xmlpi.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc("""<!DOCTYPE html PUBLIC>""")

        assert [
            (0, 2, self.tokenizers[0].tokens.xmldef.span_start),
            (2, 21, self.tokenizers[0].tokens.xmldef.span_mid),
            (21, 22, self.tokenizers[0].tokens.xmldef.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))


class TestEncDecl:
    def test_html5(self):
        assert 'UTF-8' == get_encoding(b'<meta charset="UTF-8">')
        assert 'UTF-8' == get_encoding(b"<meta charset='UTF-8'>")
        assert not  get_encoding(b"<meta charset='UTF-8>")

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
