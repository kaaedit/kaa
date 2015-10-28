from unittest.mock import patch
import kaa_testutils
from kaa.filetype.rst import rstmode


class TestRstHighlight(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = rstmode.RstMode
    TOKENIZER = rstmode.RstMode.tokenizer

    def test_inline(self):

        doc = self._getdoc("**abc**")
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.strong] * 7)

        doc = self._getdoc("*abc*")
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 5, 
            [self.TOKENIZER.tokens.emphasis] * 5)

        doc = self._getdoc('``abc``')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.literal] * 7)

        doc = self._getdoc('`abc`_')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6, 
            [self.TOKENIZER.tokens.interpreted] * 6)

        doc = self._getdoc('abc_')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 4, 
            [self.TOKENIZER.tokens.reference] * 4)

        doc = self._getdoc('_`abc`')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6, 
            [self.TOKENIZER.tokens.target] * 6)

        doc = self._getdoc('|abc|')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 5, 
            [self.TOKENIZER.tokens.substitution] * 5)

        doc = self._getdoc('[abc]_')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6, 
            [self.TOKENIZER.tokens.citation] * 6)

    def test_inline_delim(self):

        doc = self._getdoc('abc*abc')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.default] * 7)

        doc = self._getdoc('*abc*abc')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.emphasis] * 7)


    def test_header(self):
        doc = self._getdoc('--\nab\n---')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 9, 
            [self.TOKENIZER.tokens.header1] * 9)

    def test_block(self):
        doc = self._getdoc('abc:: \na')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 8, 
            [self.TOKENIZER.tokens.default] * 3 +
            [self.TOKENIZER.tokens.block] * 4 +
            [self.TOKENIZER.tokens.default])

    def test_directive(self):
        doc = self._getdoc('.. abc:: 111\n 222\n333')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 21, 
            [self.TOKENIZER.tokens.directive] * 18 +
            [self.TOKENIZER.tokens.default] * 3)


    def test_table(self):
        doc = self._getdoc('+=+\n| |')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.table_border] * 4 +
            [self.TOKENIZER.tokens.table_row] * 3)

