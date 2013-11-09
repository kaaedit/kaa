import kaa_testutils
from kaa import highlight
from kaa.filetype.markdown import markdownmode


class TestMarkdownHighlight(kaa_testutils._TestDocBase):
    tokenizers = [markdownmode.build_tokenizer()]
    tokens = tokenizers[0].tokens
    
    def test_header1(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('abc\n---')
        assert [
            (0, 7, self.tokens.header1.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_header2(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('# abc')
        assert [
            (0, 5, self.tokens.header2.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_codeblock(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('    abc')
        assert [
            (0, 7, self.tokens.codeblock.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_hr(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('----')
        assert [
            (0, 4, self.tokens.hr.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_link(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('[link][link]')
        assert [
            (0, 6, self.tokens.link.text),
            (6, 12, self.tokens.link.link),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('[link](url)')
        assert [
            (0, 6, self.tokens.link.text),
            (6, 11, self.tokens.link.url),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('[link](url "te)xt")')
        assert [
            (0, 6, self.tokens.link.text),
            (6, 19, self.tokens.link.url),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('[link]:')
        assert [
            (0, 7, self.tokens.link.text),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_image(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('![link][link]')
        assert [
            (0, 7, self.tokens.image.text),
            (7, 13, self.tokens.image.link),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('![link](url)')
        assert [
            (0, 7, self.tokens.image.text),
            (7, 12, self.tokens.image.url),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_emphasis(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('**text**')
        assert [
            (0, 2, self.tokens.strong1.span_start),
            (2, 6, self.tokens.strong1.span_mid),
            (6, 8, self.tokens.strong1.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('__text__')
        assert [
            (0, 2, self.tokens.strong2.span_start),
            (2, 6, self.tokens.strong2.span_mid),
            (6, 8, self.tokens.strong2.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('*text*')
        assert [
            (0, 1, self.tokens.emphasis1.span_start),
            (1, 5, self.tokens.emphasis1.span_mid),
            (5, 6, self.tokens.emphasis1.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('_text_')
        assert [
            (0, 1, self.tokens.emphasis2.span_start),
            (1, 5, self.tokens.emphasis2.span_mid),
            (5, 6, self.tokens.emphasis2.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('``text``')
        assert [
            (0, 2, self.tokens.code1.span_start),
            (2, 6, self.tokens.code1.span_mid),
            (6, 8, self.tokens.code1.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('`text`')
        assert [
            (0, 1, self.tokens.code2.span_start),
            (1, 5, self.tokens.code2.span_mid),
            (5, 6, self.tokens.code2.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))


