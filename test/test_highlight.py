import kaa_testutils
from kaa import highlight


class TestKeyword(kaa_testutils._TestDocBase):
    def test_keyword(self):
        kwds = highlight.Keywords('keywords', 'keyword', ['if', 'while', 'for'])
        tokenizer = highlight.Tokenizer([kwds])

        doc = self._getdoc('if while for ')
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        assert [
            (0, 2, kwds.tokenid),
            (2, 3, hl.tokenizers[0].nulltoken),
            (3, 8, kwds.tokenid),
            (8, 9, hl.tokenizers[0].nulltoken),
            (9, 12, kwds.tokenid),
            (12, 13, hl.tokenizers[0].nulltoken)
        ] == list((f, t, style) for f, t, style in hl.highlight(doc, 0))

    def test_keyword_resume(self):
        kwds = highlight.Keywords('keywords', 'style', ['if', 'while', 'for'])
        tokenizer = highlight.Tokenizer([kwds])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc('   while')
        doc.styles.setints(3, 8, kwds.tokenid)

        assert 3 == kwds.resume_pos(hl, tokenizer, doc, 5)

    def test_span(self):
        span = highlight.Span('str', 'style', '"""', '"""')
        tokenizer = highlight.Tokenizer([span])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(' """ """ ')
        ret = list((f, t, style) for f, t, style in hl.highlight(doc, 0))
        assert [
            (0, 1, hl.tokenizers[0].nulltoken),
            (1, 4, span.span_start),
            (4, 5, span.span_mid),
            (5, 8, span.span_end),
            (8, 9, hl.tokenizers[0].nulltoken),] == ret

        span = highlight.Span('str', 'style', '"', '"')
        tokenizer = highlight.Tokenizer([span])

        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc('"" ""')
        ret = list((f, t, style) for f, t, style in hl.highlight(doc, 0))
        assert [
            (0, 1, span.span_start),
            (1, 2, span.span_end),
            (2, 3, hl.tokenizers[0].nulltoken),
            (3, 4, span.span_start),
            (4, 5, span.span_end),] == ret

    def test_span_escape(self):
        span = highlight.Span('str', 'style', '"""', '"""', '\\')
        tokenizer = highlight.Tokenizer([span])

        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'"""\""""')
        ret = list((f, t, style) for f, t, style in hl.highlight(doc, 0))
        assert [
            (0, 3, span.span_start),
            (3, 5, span.span_mid),
            (5, 8, span.span_end),] == ret

    def test_span_noclose(self):
        kwds = highlight.Span('str', 'style', '"', '"', '\\')
        tokenizer = highlight.Tokenizer([kwds])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'"\"abcdefg')
        ret = list((f, t, style) for f, t, style in hl.highlight(doc, 0))
        assert [
            (0, 1, kwds.span_start),
            (1, 10, kwds.span_mid),] == ret

    def test_span_resume(self):
        span = highlight.Span('str', 'style', '"', '"', None)
        tokenizer = highlight.Tokenizer([span])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'   "TEXT"')
        doc.styles.setints(3, 9, span.span_start)

        assert 3 == span.resume_pos(hl, tokenizer, doc, 5)

    def test_subsection(self):

        kwd = highlight.Keywords('keywords', 'style', ['abcdefg'])
        sub = highlight.Tokenizer([kwd])

        brace = highlight.SubSection('sub', 'style', r'\(', sub)
        tokenizer = highlight.Tokenizer([brace])

        hl = highlight.Highlighter(tokenizers=[tokenizer, sub])

        doc = self._getdoc(r'   (abcdefg   ')
        ret = list((f, t, style) for f, t, style in hl.highlight(doc, 0))
        assert [
            (0, 3, hl.tokenizers[0].nulltoken),
            (3, 4, brace.section_start),
            (4, 11, kwd.tokenid),
            (11, 14, hl.tokenizers[1].nulltoken)] == ret

    def test_subsection_resume(self):
        sub = highlight.Tokenizer([])

        brace = highlight.SubSection('sub', 'style', r'\(', sub)
        tokenizer = highlight.Tokenizer([brace])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'   (')
        doc.styles.setints(3, 4, brace.section_start)

        assert 3 == brace.resume_pos(hl, tokenizer, doc, 3)

    def test_endsection(self):
        end = highlight.EndSection('sub', 'style', r'\)')
        tokenizer = highlight.Tokenizer([end])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'   )')
        doc.styles.setints(3, 4, end.section_end)

        assert 3 == end.resume_pos(hl, tokenizer, doc, 3)

    def test_endsection_resume(self):
        end = highlight.EndSection('sub', 'style', r'\)')
        tokenizer = highlight.Tokenizer([end])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'   )')
        doc.styles.setints(3, 4, end.section_end)

        assert 3 == end.resume_pos(hl, tokenizer, doc, 3)

    def test_subtokenizer(self):
        kwds = highlight.Keywords('keywords', 'keyword', ['a', 'b'])
        tokenizer1 = highlight.Tokenizer([kwds])
        sub1 = highlight.SubTokenizer('sub', 'a', tokenizer1)
        tokenizer = highlight.Tokenizer([sub1])
        hl = highlight.Highlighter(tokenizers=[tokenizer])

        doc = self._getdoc(r'a b c a b c')
        ret = list((f, t, style) for f, t, style in hl.highlight(doc, 0))
        assert [
            (0, 1, kwds.tokenid),
            (1, 2, tokenizer1.nulltoken),
            (2, 3, kwds.tokenid),
            (3, 6, tokenizer1.nulltoken),
            (6, 7, kwds.tokenid),
            (7, 8, tokenizer1.nulltoken),
            (8, 9, kwds.tokenid),
            (9, 11, tokenizer1.nulltoken),
        ] == ret

class TestSection:
    def test_walk(self):
        section1 = highlight.Section(None, None)
        section2 = highlight.Section(None, None)
        section3 = highlight.Section(None, None)
        section4 = highlight.Section(None, None)
        section5 = highlight.Section(None, None)
        section6 = highlight.Section(None, None)
        section7 = highlight.Section(None, None)
        section8 = highlight.Section(None, None)
        section9 = highlight.Section(None, None)
        section10 = highlight.Section(None, None)


        section1.add(section2)
        section1.add(section3)

        section3.add(section4)
        section3.add(section5)

        section5.add(section6)
        section5.add(section7)

        section1.add(section8)
        section1.add(section9)
        section9.add(section10)

        assert [section1, section2, section3, section4,
                section5, section6, section7, section8,
                section9, section10, ] == list(section1.walk())

    def _newsection(self, start):
        section = highlight.Section(start, None)
        return section

    def test_getsection(self):
        section1 = self._newsection(0)
        section2 = self._newsection(1)
        section3 = self._newsection(2)

        section1.add(section2)
        section2.add(section3)

        assert section1.get_section(0) is section1
        assert section1.get_section(1) is section2
        assert section1.get_section(2) is section3

    def test_deleteafter(self):
        section1 = self._newsection(0)
        section2 = self._newsection(1)
        section3 = self._newsection(2)
        section4 = self._newsection(3)
        section5 = self._newsection(4)
        section6 = self._newsection(5)
        section7 = self._newsection(6)
        section8 = self._newsection(6)
        section9 = self._newsection(6)
        section10 = self._newsection(7)
        section11 = self._newsection(8)
        section12 = self._newsection(9)
        section13 = self._newsection(10)

        section1.add(section2)
        section2.add(section3)
        section2.add(section4)
        section2.add(section5)
        section1.add(section6)
        section1.add(section7)
        section7.add(section8)
        section8.add(section9)
        section8.add(section10)
        section8.add(section11)
        section8.add(section12)
        section7.add(section12)

        assert section1.get_section(2) is section3
        aa = section1.get_section(8)
        assert section1.get_section(8) is section11

        section1.delete_after(8)
        assert section7.children == [section8]
        assert section1.children == [section2, section6, section7]

        section1.delete_after(3)
        assert section2.children == [section3, section4]
        assert section1.children == [section2]


class TestHighlight(kaa_testutils._TestDocBase):
    def get_highliter(self):
        kwds = highlight.Keywords("jskeyword", 'style', ['if', 'while'])
        lit = highlight.Span('string', 'style', '"', '"', escape='\\')
        endsection = highlight.EndSection('endscript', 'style', '</script>')
        jstoken = highlight.Tokenizer([kwds, lit, endsection])

        elem = highlight.Span('comment', 'style', '<!--', '-->')
        scriptelem = highlight.SubSection('beginscript', 'style', '<script>', tokenizer=jstoken)
        htmltoken = highlight.Tokenizer([elem, scriptelem])

        hl = highlight.Highlighter(tokenizers=[htmltoken, jstoken])
        return hl, kwds, lit, endsection, elem, scriptelem

    def get_doc(self):
        return self._getdoc(r'abc<script>if while</script>if while<!-- comment -->')

    def test_highlight(self):

        hl, kwds, lit, endsection, elem, scriptelem = self.get_highliter()
        doc = self.get_doc()

        tokens = list(hl.highlight(doc, 0))
        assert [
            (0, 3, hl.tokenizers[0].nulltoken),
            (3, 11, scriptelem.section_start),
            (11, 13, kwds.tokenid),
            (13, 14, hl.tokenizers[1].nulltoken),
            (14, 19, kwds.tokenid),
            (19, 28, endsection.section_end),
            (28, 36, hl.tokenizers[0].nulltoken),
            (36, 40, elem.span_start),
            (40, 49, elem.span_mid),
            (49, 52, elem.span_end),
        ] == tokens

    def test_resume(self):
        hl, kwds, lit, endsection, elem, scriptelem = self.get_highliter()
        doc = self.get_doc()
        list(hl.highlight(doc, 0))
        doc.styles.setints(14, 19, kwds.tokenid)

        assert 0 == hl.get_resume_pos(doc, 0)
        assert 0 == hl.get_resume_pos(doc, 1)
        assert 14 == hl.get_resume_pos(doc, 16)
        assert 19 == hl.get_resume_pos(doc, 28)
        assert 19 == hl.get_resume_pos(doc, 29)

        tokens = list(hl.highlight(doc, 19))
        assert [
            (19, 28, endsection.section_end),
            (28, 36, hl.tokenizers[0].nulltoken),
            (36, 40, elem.span_start),
            (40, 49, elem.span_mid),
            (49, 52, elem.span_end),
        ] == tokens

    def test_update(self):

        hl, kwds, lit, endsection, elem, scriptelem = self.get_highliter()
        doc = self.get_doc()
        doc.mode.highlight = hl
        doc.mode.highlight.update_style(doc)

        assert ([hl.tokenizers[0].nulltoken]*3 + [scriptelem.section_start]*8 + [kwds.tokenid]*2 +
                [hl.tokenizers[1].nulltoken] + [kwds.tokenid]*5 + [endsection.section_end]*9 +
                [hl.tokenizers[0].nulltoken]*8 + [elem.span_start]*4 + [elem.span_mid]*9 +
                [elem.span_end]*3)  == doc.styles.getints(0, len(doc.styles))

        doc.replace(16, 17, 'x') # while -> whxle
        doc.mode.highlight.update_style(doc)

        assert ([hl.tokenizers[0].nulltoken]*3 + [scriptelem.section_start]*8 + [kwds.tokenid]*2 +
                [hl.tokenizers[1].nulltoken] + [hl.tokenizers[1].nulltoken]*5 + [endsection.section_end]*9 +
                [hl.tokenizers[0].nulltoken]*8 + [elem.span_start]*4 + [elem.span_mid]*9 +
                [elem.span_end]*3)  == doc.styles.getints(0, len(doc.styles))

