import kaa_testutils
from kaa.filetype.markdown.markdownmode import MarkdownMode


class TestMarkdownHighlight(kaa_testutils._TestDocBase):
    DEFAULTMODECLASS = MarkdownMode
    TOKENIZER = MarkdownMode.tokenizer

    def test_header1(self):
        doc = self._getdoc('abc\n---')
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.header1] * 7)

    def test_header2(self):
        doc = self._getdoc('# abc')
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 5, 
            [self.TOKENIZER.tokens.header2] * 5)

    def test_hr(self):
        doc = self._getdoc('----')
        doc.mode.run_tokenizer(None)

        kaa_testutils.check_style(doc, 0, 4, 
            [self.TOKENIZER.tokens.hr] * 4)

    def test_link(self):
        doc = self._getdoc('[link][link]')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 12, 
            [self.TOKENIZER.tokens.link]*12)

        doc = self._getdoc('[link](url)')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 11, 
            [self.TOKENIZER.tokens.link]*7 + 
            [self.TOKENIZER._LinkTokenizer.tokens.default]*3+
            [self.TOKENIZER._LinkTokenizer.tokens.close]*1)

        doc = self._getdoc('[link](url "te)xt")')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 19, 
            [self.TOKENIZER.tokens.link]*7 + 
            [self.TOKENIZER._LinkTokenizer.tokens.default]*4+
            [self.TOKENIZER._LinkTokenizer.tokens.desc]*7+
            [self.TOKENIZER._LinkTokenizer.tokens.close]*1)

        doc = self._getdoc('[link]:')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7, 
            [self.TOKENIZER.tokens.link]*7)

    def test_image(self):
        doc = self._getdoc('![link][link]')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 13,
            [self.TOKENIZER.tokens.link]*13)

        doc = self._getdoc('![link](url)')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 12,
            [self.TOKENIZER.tokens.link]*8 + 
            [self.TOKENIZER._LinkTokenizer.tokens.default]*3 + 
            [self.TOKENIZER._LinkTokenizer.tokens.close]*1)

    def test_emphasis(self):
        doc = self._getdoc('**text**')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 8,
            [self.TOKENIZER.tokens.strong1]*8)

        doc = self._getdoc('__text__')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 8,
            [self.TOKENIZER.tokens.strong2]*8)

        doc = self._getdoc('*text*')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6,
            [self.TOKENIZER.tokens.emphasis1]*6)

        doc = self._getdoc('_text_')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6,
            [self.TOKENIZER.tokens.emphasis2]*6)

    def test_literal(self):
        doc = self._getdoc('`text`')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6,
            [self.TOKENIZER.tokens.code3]*6)

        doc = self._getdoc('```\ntext\n```\n')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 13,
            [self.TOKENIZER.tokens.code2]*13)

        doc = self._getdoc('` text`')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 7,
            [self.TOKENIZER.tokens.default]*6 +
            [self.TOKENIZER.tokens.code3])

        doc = self._getdoc('    text\na')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 10,
            [self.TOKENIZER.tokens.code1]*8 +
            [self.TOKENIZER.tokens.default]*2)

    def test_list(self):
        doc = self._getdoc('* abc')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 5,
            [self.TOKENIZER.tokens.list]*2 +
            [self.TOKENIZER.tokens.default]*3)

        doc = self._getdoc('1. abc')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 6,
            [self.TOKENIZER.tokens.list]*3 +
            [self.TOKENIZER.tokens.default]*3)

        doc = self._getdoc('1. abc\n    * def')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 16,
            [self.TOKENIZER.tokens.list]*3 +
            [self.TOKENIZER.tokens.default]*4+
            [self.TOKENIZER.tokens.list]*6+
            [self.TOKENIZER.tokens.default]*3)

        doc = self._getdoc('1. abc\na\n    * def')
        doc.mode.run_tokenizer(None)
        kaa_testutils.check_style(doc, 0, 18,
            [self.TOKENIZER.tokens.list]*3 +
            [self.TOKENIZER.tokens.default]*6+
            [self.TOKENIZER.tokens.code1]*9)

