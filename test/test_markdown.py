import kaa_testutils
from kaa.filetype.markdown.markdownmode import MarkdownTokenizer


class TestMarkdownHighlight(kaa_testutils._TestDocBase):

    def test_header1(self):
        doc = self._getdoc('abc\n---')
        assert [
            (0, 7, MarkdownTokenizer.tokens.header1.styleid_token),
        ] == list(MarkdownTokenizer.run(doc, 0))

    def test_header2(self):
        doc = self._getdoc('# abc')
        assert [
            (0, 5, MarkdownTokenizer.tokens.header2.styleid_token),
        ] == list(MarkdownTokenizer.run(doc, 0))

    def test_hr(self):
        doc = self._getdoc('----')
        assert [
            (0, 4, MarkdownTokenizer.tokens.hr.styleid_token),
        ] == list(MarkdownTokenizer.run(doc, 0))

    def test_link(self):
        doc = self._getdoc('[link][link]')
        assert [
            (0, 1, MarkdownTokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.link.styleid_span),
            (5, 6, MarkdownTokenizer.tokens.link.styleid_span),
            (6, 7, MarkdownTokenizer.tokens.link.styleid_span),
            (7, 11, MarkdownTokenizer.tokens.link.styleid_span),
            (11, 12, MarkdownTokenizer.tokens.link.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('[link](url)')
        assert [
            (0, 1, MarkdownTokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.link.styleid_span),
            (5, 7, MarkdownTokenizer.tokens.link.styleid_span),
            (7, 10, MarkdownTokenizer._LinkTokenizer.styleid_default),
            (10, 11, MarkdownTokenizer._LinkTokenizer.tokens.close.styleid_token),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('[link](url "te)xt")')
        assert [
            (0, 1, MarkdownTokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.link.styleid_span),
            (5, 7, MarkdownTokenizer.tokens.link.styleid_span),
            (7, 11, MarkdownTokenizer._LinkTokenizer.styleid_default),
            (11, 12, MarkdownTokenizer._LinkTokenizer.tokens.desc.styleid_span),
            (12, 17, MarkdownTokenizer._LinkTokenizer.tokens.desc.styleid_span),
            (17, 18, MarkdownTokenizer._LinkTokenizer.tokens.desc.styleid_span),
            (18, 19, MarkdownTokenizer._LinkTokenizer.tokens.close.styleid_token)
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('[link]:')
        assert [
            (0, 1, MarkdownTokenizer.tokens.link.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.link.styleid_span),
            (5, 7, MarkdownTokenizer.tokens.link.styleid_span)
        ] == list(MarkdownTokenizer.run(doc, 0))

    def test_image(self):
        doc = self._getdoc('![link][link]')
        assert [
            (0, 2, MarkdownTokenizer.tokens.link.styleid_span),
            (2, 6, MarkdownTokenizer.tokens.link.styleid_span),
            (6, 7, MarkdownTokenizer.tokens.link.styleid_span),
            (7, 8, MarkdownTokenizer.tokens.link.styleid_span),
            (8, 12, MarkdownTokenizer.tokens.link.styleid_span),
            (12, 13, MarkdownTokenizer.tokens.link.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('![link](url)')
        assert [
            (0, 2, MarkdownTokenizer.tokens.link.styleid_span),
            (2, 6, MarkdownTokenizer.tokens.link.styleid_span),
            (6, 8, MarkdownTokenizer.tokens.link.styleid_span),
            (8, 11, MarkdownTokenizer._LinkTokenizer.styleid_default),
            (11, 12, MarkdownTokenizer._LinkTokenizer.tokens.close.styleid_token),
        ] == list(MarkdownTokenizer.run(doc, 0))

    def test_emphasis(self):
        doc = self._getdoc('**text**')
        assert [
            (0, 2, MarkdownTokenizer.tokens.strong1.styleid_span),
            (2, 6, MarkdownTokenizer.tokens.strong1.styleid_span),
            (6, 8, MarkdownTokenizer.tokens.strong1.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('__text__')
        assert [
            (0, 2, MarkdownTokenizer.tokens.strong2.styleid_span),
            (2, 6, MarkdownTokenizer.tokens.strong2.styleid_span),
            (6, 8, MarkdownTokenizer.tokens.strong2.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('*text*')
        assert [
            (0, 1, MarkdownTokenizer.tokens.emphasis1.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.emphasis1.styleid_span),
            (5, 6, MarkdownTokenizer.tokens.emphasis1.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('_text_')
        assert [
            (0, 1, MarkdownTokenizer.tokens.emphasis2.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.emphasis2.styleid_span),
            (5, 6, MarkdownTokenizer.tokens.emphasis2.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

    def test_literal(self):
        doc = self._getdoc('`text`')

        assert [
            (0, 1, MarkdownTokenizer.tokens.code3.styleid_span),
            (1, 5, MarkdownTokenizer.tokens.code3.styleid_span),
            (5, 6, MarkdownTokenizer.tokens.code3.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('```\ntext\n```\n')
        assert [
            (0, 3, MarkdownTokenizer.tokens.code1.styleid_span),
            (3, 9, MarkdownTokenizer.tokens.code1.styleid_span),
            (9, 13, MarkdownTokenizer.tokens.code1.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('` text`')
        assert [
            (0, 6, MarkdownTokenizer.styleid_default),
            (6, 7, MarkdownTokenizer.tokens.code3.styleid_span),
        ] == list(MarkdownTokenizer.run(doc, 0))

        doc = self._getdoc('    text\na')
        assert [
            (0, 4, MarkdownTokenizer.tokens.code2.styleid_span),
            (4, 8, MarkdownTokenizer.tokens.code2.styleid_span),
            (8, 10, MarkdownTokenizer.styleid_default),
        ] == list(MarkdownTokenizer.run(doc, 0))
