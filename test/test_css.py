import kaa_testutils
from kaa import highlight
from kaa.filetype.css import cssmode


class TestHTMLHighlight(kaa_testutils._TestDocBase):
    tokenizers = [cssmode.build_tokenizer()]

    def test_comment(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('/* ')

        assert [
            (0, 2, self.tokenizers[0].tokens[0].span_comment_begin),
            (2, 3, self.tokenizers[0].tokens[0].span_comment),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_selector(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('/* */selector/**/selector')

        assert [
            (0, 2, self.tokenizers[0].tokens[0].span_comment_begin),
            (2, 3, self.tokenizers[0].tokens[0].span_comment),
            (3, 5, self.tokenizers[0].tokens[0].span_comment_end),
            (5, 13, self.tokenizers[0].tokens[0].span_selector),
            (13, 15, self.tokenizers[0].tokens[0].span_comment_begin),
            (15, 17, self.tokenizers[0].tokens[0].span_comment_end),
            (17, 25, self.tokenizers[0].tokens[0].span_selector),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_block(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('{')

        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_block(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('{ abc:')

        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 5, self.tokenizers[0].tokens[0].span_propname),
            (5, 6, self.tokenizers[0].tokens[0].span_colon),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('{abc}')

        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 4, self.tokenizers[0].tokens[0].span_propname),
            (4, 5, self.tokenizers[0].tokens[0].span_close_brace),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('{/**/a/**/bc/**/}/**/')

        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 3, self.tokenizers[0].tokens[0].span_comment_begin),
            (3, 5, self.tokenizers[0].tokens[0].span_comment_end),
            (5, 6, self.tokenizers[0].tokens[0].span_propname),
            (6, 8, self.tokenizers[0].tokens[0].span_comment_begin),
            (8, 10, self.tokenizers[0].tokens[0].span_comment_end),
            (10, 12, self.tokenizers[0].tokens[0].span_propname),
            (12, 14, self.tokenizers[0].tokens[0].span_comment_begin),
            (14, 16, self.tokenizers[0].tokens[0].span_comment_end),
            (16, 17, self.tokenizers[0].tokens[0].span_close_brace),
            (17, 19, self.tokenizers[0].tokens[0].span_comment_begin),
            (19, 21, self.tokenizers[0].tokens[0].span_comment_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_prop(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('{abc:def')
        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 4, self.tokenizers[0].tokens[0].span_propname),
            (4, 5, self.tokenizers[0].tokens[0].span_colon),
            (5, 8, self.tokenizers[0].tokens[0].span_propvalue),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('{abc:def;ghi:jkl/**/;}')
        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 4, self.tokenizers[0].tokens[0].span_propname),
            (4, 5, self.tokenizers[0].tokens[0].span_colon),
            (5, 8, self.tokenizers[0].tokens[0].span_propvalue),
            (8, 9, self.tokenizers[0].tokens[0].span_semicolon),
            (9, 12, self.tokenizers[0].tokens[0].span_propname),
            (12, 13, self.tokenizers[0].tokens[0].span_colon),
            (13, 16, self.tokenizers[0].tokens[0].span_propvalue),
            (16, 18, self.tokenizers[0].tokens[0].span_comment_begin),
            (18, 20, self.tokenizers[0].tokens[0].span_comment_end),
            (20, 21, self.tokenizers[0].tokens[0].span_semicolon),
            (21, 22, self.tokenizers[0].tokens[0].span_close_brace),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_string(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)

        doc = self._getdoc('"aaa"')
        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_string_begin),
            (1, 4, self.tokenizers[0].tokens[0].span_string),
            (4, 5, self.tokenizers[0].tokens[0].span_string_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc(r'"\""')
        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_string_begin),
            (1, 3, self.tokenizers[0].tokens[0].span_string),
            (3, 4, self.tokenizers[0].tokens[0].span_string_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('{"aaa"}')
        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 2, self.tokenizers[0].tokens[0].span_string_begin),
            (2, 5, self.tokenizers[0].tokens[0].span_string),
            (5, 6, self.tokenizers[0].tokens[0].span_string_end),
            (6, 7, self.tokenizers[0].tokens[0].span_close_brace),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

        doc = self._getdoc('{a:"aaa"}')
        assert [
            (0, 1, self.tokenizers[0].tokens[0].span_open_brace),
            (1, 2, self.tokenizers[0].tokens[0].span_propname),
            (2, 3, self.tokenizers[0].tokens[0].span_colon),
            (3, 4, self.tokenizers[0].tokens[0].span_string_begin),
            (4, 7, self.tokenizers[0].tokens[0].span_string),
            (7, 8, self.tokenizers[0].tokens[0].span_string_end),
            (8, 9, self.tokenizers[0].tokens[0].span_close_brace),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))
