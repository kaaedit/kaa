import kaa_testutils
from kaa.filetype.css import cssmode


class TestCSSHighlight(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = cssmode.CSSMode

    def test_css(self):
        doc = self._getdoc('sel{abc:def;}')
        doc.mode.run_tokenizer(None)
        tokenizer = cssmode.CSSMode.tokenizer
        assert doc.styles.getints(0, 3) == [tokenizer.styleid_default]*3
        assert doc.styles.getints(3, 4) == [tokenizer.tokens.ruleset.styleid_token]*1
        assert doc.styles.getints(4, 8) == [tokenizer.PropTokenizer.tokens.propname.styleid_token]*4
        assert doc.styles.getints(8, 11) == [tokenizer.PropTokenizer.PropValueTokenizer.styleid_default]*3
        print(11111111111111, tokenizer.PropTokenizer.PropValueTokenizer.tokens.terminate.styleid_token)
        assert doc.styles.getints(11, 12) == [tokenizer.PropTokenizer.PropValueTokenizer.tokens.terminate.styleid_token]*1
#        assert doc.styles.getints(11, 12) == [tokenizer.PropTokenizer.tokens.propname.styleid_token]*1
        assert doc.styles.getints(12, 13) == [tokenizer.tokens.ruleset.styleid_token]*1


