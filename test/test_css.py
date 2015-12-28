import kaa_testutils
from kaa.filetype.css import cssmode


class TestCSSHighlight(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = cssmode.CSSMode

    def test_propvalue(self):
        doc = self._getdoc('sel{abc:.1em;def:ghi}')
        doc.mode.run_tokenizer(None)
        tokenizer = cssmode.CSSMode.tokenizer

        kaa_testutils.check_style(doc, 0, 21, 
            [tokenizer.tokens.default] * 3 +
            [tokenizer.tokens.ruleset] * 1 +
            [tokenizer.PropTokenizer.tokens.propname] * 4 +
            [tokenizer.PropTokenizer.PropValueTokenizer.tokens.number] * 4 +
            [tokenizer.PropTokenizer.PropValueTokenizer.tokens.terminate_value] * 1 +
            [tokenizer.PropTokenizer.tokens.propname] * 4 +
            [tokenizer.PropTokenizer.PropValueTokenizer.tokens.string] * 3 +
            [tokenizer.PropTokenizer.tokens.terminate_name] * 1
        )

    def test_no_media(self):
        doc = self._getdoc('sel{abc:def;}')
        doc.mode.run_tokenizer(None)
        tokenizer = cssmode.CSSMode.tokenizer

        kaa_testutils.check_style(doc, 0, 13, 
            [tokenizer.tokens.default] * 3 +
            [tokenizer.tokens.ruleset] * 1 +
            [tokenizer.PropTokenizer.tokens.propname] * 4 +
            [tokenizer.PropTokenizer.PropValueTokenizer.tokens.string] * 3 +
            [tokenizer.PropTokenizer.PropValueTokenizer.tokens.terminate_value] * 1 +
            [tokenizer.PropTokenizer.tokens.terminate_name] * 1
        )

    def test_media(self):
        doc = self._getdoc('@media a{b{c:d}}@media e{f{g:h}}')
        doc.mode.run_tokenizer(None)

        tokenizer = cssmode.CSSMode.tokenizer
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 32, 
            [tokenizer.tokens.media] * 9 +
            [tokenizer.MediaCSSTokenizer.tokens.default] * 1 +
            [tokenizer.MediaCSSTokenizer.tokens.ruleset] * 1 +
            [tokenizer.MediaCSSTokenizer.PropTokenizer.tokens.propname] * 2 +
            [tokenizer.MediaCSSTokenizer.PropTokenizer.PropValueTokenizer.tokens.string] * 1 +
            [tokenizer.MediaCSSTokenizer.PropTokenizer.tokens.terminate_name] * 1 +
            [tokenizer.MediaCSSTokenizer.tokens.terminate_media] * 1 +

            [tokenizer.tokens.media] * 9 +
            [tokenizer.MediaCSSTokenizer.tokens.default] * 1 +
            [tokenizer.MediaCSSTokenizer.tokens.ruleset] * 1 +
            [tokenizer.MediaCSSTokenizer.PropTokenizer.tokens.propname] * 2 +
            [tokenizer.MediaCSSTokenizer.PropTokenizer.PropValueTokenizer.tokens.string] * 1 +
            [tokenizer.MediaCSSTokenizer.PropTokenizer.tokens.terminate_name] * 1 +
            [tokenizer.MediaCSSTokenizer.tokens.terminate_media] * 1
            )
