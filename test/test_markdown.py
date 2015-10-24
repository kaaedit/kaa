import kaa_testutils
from kaa.filetype.markdown.markdownmode import MarkdownMode


class TestMarkdownHighlight(kaa_testutils._TestDocBase):

    def test_header1(self):
        doc = self._getdoc('abc\n---')
        assert [
            (0, 7, MarkdownMode.tokenizer.tokens.header1.styleid_token),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

    def test_header2(self):
        doc = self._getdoc('# abc')
        assert [
            (0, 5, MarkdownMode.tokenizer.tokens.header2.styleid_token),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

    def test_hr(self):
        doc = self._getdoc('----')
        assert [
            (0, 4, MarkdownMode.tokenizer.tokens.hr.styleid_token),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

    def test_link(self):
        doc = self._getdoc('[link][link]')
        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (5, 6, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (6, 7, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (7, 11, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (11, 12, MarkdownMode.tokenizer.tokens.link.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('[link](url)')
        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (5, 7, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (7, 10, MarkdownMode.tokenizer._LinkTokenizer.styleid_default),
            (10, 11, MarkdownMode.tokenizer._LinkTokenizer.tokens.close.styleid_token),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('[link](url "te)xt")')
        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (5, 7, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (7, 11, MarkdownMode.tokenizer._LinkTokenizer.styleid_default),
            (11, 12, MarkdownMode.tokenizer._LinkTokenizer.tokens.desc.styleid_span),
            (12, 17, MarkdownMode.tokenizer._LinkTokenizer.tokens.desc.styleid_span),
            (17, 18, MarkdownMode.tokenizer._LinkTokenizer.tokens.desc.styleid_span),
            (18, 19, MarkdownMode.tokenizer._LinkTokenizer.tokens.close.styleid_token)
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('[link]:')
        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (5, 7, MarkdownMode.tokenizer.tokens.link.styleid_span)
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

    def test_image(self):
        doc = self._getdoc('![link][link]')
        assert [
            (0, 2, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (2, 6, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (6, 7, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (7, 8, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (8, 12, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (12, 13, MarkdownMode.tokenizer.tokens.link.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('![link](url)')
        assert [
            (0, 2, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (2, 6, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (6, 8, MarkdownMode.tokenizer.tokens.link.styleid_span),
            (8, 11, MarkdownMode.tokenizer._LinkTokenizer.styleid_default),
            (11, 12, MarkdownMode.tokenizer._LinkTokenizer.tokens.close.styleid_token),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

    def test_emphasis(self):
        doc = self._getdoc('**text**')
        assert [
            (0, 2, MarkdownMode.tokenizer.tokens.strong1.styleid_span),
            (2, 6, MarkdownMode.tokenizer.tokens.strong1.styleid_span),
            (6, 8, MarkdownMode.tokenizer.tokens.strong1.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('__text__')
        assert [
            (0, 2, MarkdownMode.tokenizer.tokens.strong2.styleid_span),
            (2, 6, MarkdownMode.tokenizer.tokens.strong2.styleid_span),
            (6, 8, MarkdownMode.tokenizer.tokens.strong2.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('*text*')
        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.emphasis1.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.emphasis1.styleid_span),
            (5, 6, MarkdownMode.tokenizer.tokens.emphasis1.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('_text_')
        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.emphasis2.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.emphasis2.styleid_span),
            (5, 6, MarkdownMode.tokenizer.tokens.emphasis2.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

    def test_literal(self):
        doc = self._getdoc('`text`')

        assert [
            (0, 1, MarkdownMode.tokenizer.tokens.code3.styleid_span),
            (1, 5, MarkdownMode.tokenizer.tokens.code3.styleid_span),
            (5, 6, MarkdownMode.tokenizer.tokens.code3.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('```\ntext\n```\n')
        assert [
            (0, 3, MarkdownMode.tokenizer.tokens.code1.styleid_span),
            (3, 9, MarkdownMode.tokenizer.tokens.code1.styleid_span),
            (9, 13, MarkdownMode.tokenizer.tokens.code1.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('` text`')
        assert [
            (0, 6, MarkdownMode.tokenizer.styleid_default),
            (6, 7, MarkdownMode.tokenizer.tokens.code3.styleid_span),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))

        doc = self._getdoc('    text\na')
        assert [
            (0, 4, MarkdownMode.tokenizer.tokens.code2.styleid_span),
            (4, 8, MarkdownMode.tokenizer.tokens.code2.styleid_span),
            (8, 10, MarkdownMode.tokenizer.styleid_default),
        ] == list(MarkdownMode.tokenizer.run(doc, 0))
