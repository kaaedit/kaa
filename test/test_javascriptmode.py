import kaa_testutils
from kaa.filetype.javascript.javascriptmode import JavaScriptMode


class TestJavascriptHighlight(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = JavaScriptMode

    def test_regex(self):
        doc = self._getdoc('/abc/')
        doc.mode.run_tokenizer(None)
        assert doc.styles.getints(0, 5) == [JavaScriptMode.tokenizer.tokens.regex.styleid_span]*5

    def test_not_regex(self):
        doc = self._getdoc('if a /abc/')
        doc.mode.run_tokenizer(None)

        assert doc.styles.getints(0, 2) == [JavaScriptMode.tokenizer.tokens.keyword.styleid_token]*2
        assert doc.styles.getints(2, 10) == [JavaScriptMode.tokenizer.styleid_default]*8
