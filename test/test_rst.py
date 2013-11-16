from unittest.mock import patch
import kaa_testutils
from kaa import highlight
from kaa.filetype.rst import rstmode


class TestRstHighlight(kaa_testutils._TestDocBase):
    tokenizers = [rstmode.build_tokenizer()]
    tokens = tokenizers[0].tokens
    
    def test_inline(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('**abc**')
        assert [
            (0, 2, self.tokens.strong.span_start),
            (2, 5, self.tokens.strong.span_mid),
            (5, 7, self.tokens.strong.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('*abc*')
        assert [
            (0, 1, self.tokens.emphasis.span_start),
            (1, 4, self.tokens.emphasis.span_mid),
            (4, 5, self.tokens.emphasis.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('``abc``')
        assert [
            (0, 2, self.tokens.literal.span_start),
            (2, 5, self.tokens.literal.span_mid),
            (5, 7, self.tokens.literal.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('`abc`_')
        assert [
            (0, 1, self.tokens.interpreted.span_start),
            (1, 4, self.tokens.interpreted.span_mid),
            (4, 6, self.tokens.interpreted.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('abc_')
        assert [
            (0, 4, self.tokens.reference.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('_`abc`')
        assert [
            (0, 3, self.tokens.target.span_start),
            (3, 5, self.tokens.target.span_mid),
            (5, 6, self.tokens.target.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('|abc|')
        assert [
            (0, 5, self.tokens.substitution.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('[abc]_')
        assert [
            (0, 6, self.tokens.citation.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_inline_delim(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        
        doc = self._getdoc('abc*abc')
        assert [
            (0, 3, self.tokenizers[0].nulltoken),
            (3, 4, self.tokenizers[0].nulltoken),
            (4, 7, self.tokenizers[0].nulltoken),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('*abc*abc')
        assert [
            (0, 1, self.tokens.emphasis.span_start),
            (1, 8, self.tokens.emphasis.span_mid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_header(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('--\nab\n---')
        assert [
            (0, 9, self.tokens.header1.tokenid),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_block(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('abc:: \n')
        assert [
            (0, 3, self.tokenizers[0].nulltoken),
            (3, 6, self.tokens.block.tokenid),
            (6, 7, self.tokenizers[0].nulltoken),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_directive(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('.. abc:: 111\n 222\n333')
        assert [
            (0,  8, self.tokens.directive.span_start),
            (8,  18, self.tokens.directive.span_mid),
            (18, 21, self.tokenizers[0].nulltoken),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_table(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        with patch.object(hl, 'get_token', return_value=self.tokens.tableborder):
            doc = self._getdoc('+=+\n| |')
            assert [
                (0,  4, self.tokens.tableborder.tokenid),
                (4,  6, self.tokens.tablerow.tokenid),
                (6,  7, self.tokens.tablerow.tokenid),
            ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))


