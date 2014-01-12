import kaa_testutils
from kaa import highlight
from kaa.filetype.javascript import javascriptmode

class TestJavascriptHighlight(kaa_testutils._TestDocBase):
    tokenizers = [javascriptmode.build_tokenizer()]

    def test_regex(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('/abc/')
        hl.update_style(doc)


        assert [
            (0, 1, self.tokenizers[0].tokens.regex.span_start),
            (1, 4, self.tokenizers[0].tokens.regex.span_mid),
            (4, 5, self.tokenizers[0].tokens.regex.span_end),
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_not_regex(self):
        hl = highlight.Highlighter(tokenizers=self.tokenizers)
        doc = self._getdoc('a /abc/')
        hl.update_style(doc)
        styles = doc.styles.getints(0, 7)
        assert styles == ([self.tokenizers[0].tokens.punctuation2.tokenid] +
                          [self.tokenizers[0].nulltoken] +
                          [self.tokenizers[0].tokens.punctuation1.tokenid] +
                          [self.tokenizers[0].tokens.punctuation2.tokenid]*3 +
                          [self.tokenizers[0].tokens.punctuation1.tokenid])

