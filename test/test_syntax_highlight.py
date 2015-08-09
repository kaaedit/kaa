import kaa_testutils
from kaa import syntax_highlight

class TestHighlight(kaa_testutils._TestDocBase):
    def test_token(self):
        doc = self._getdoc(' abc def ghi ')

        root = syntax_highlight.Root()
        keyword = syntax_highlight.Keywords(root, 'keyword', ['abc', 'ghi'])
        root.add_tokens(keyword)

        tokenizer = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 0)

        styles = list(tokenizer)
        assert styles == [
            (0, 1, root.styleid_default), 
            (1, 4, keyword.styleid_token), 
            (4, 9, root.styleid_default), 
            (9, 12, keyword.styleid_token),
            (12, 13, root.styleid_default),]

    def test_span(self):
        doc = self._getdoc(' ab\\cc def ghi ')

        root = syntax_highlight.Root()
        span1 = syntax_highlight.Span(root, 'span', 'a', 'c', escape='\\')
        span2 = syntax_highlight.Span(root, 'span', 'd', 'f', 
            capture_end=False)
        span3 = syntax_highlight.Span(root, 'span', 'g', 'i', terminates='h')
        root.add_tokens(span1, span2, span3)

        tokenizer = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 0)

        styles = list(tokenizer)
        assert styles == [
            (0, 1, root.styleid_default), 
            (1, 2, span1.styleid_begin), 
            (2, 5, span1.styleid_mid), 
            (5, 6, span1.styleid_end), 
            (6, 7, root.styleid_default), 
            (7, 8, span2.styleid_begin), 
            (8, 9, span2.styleid_mid), 
            (9, 11, root.styleid_default), 
            (11, 12, span3.styleid_begin), 
            (12, 15, root.styleid_default), 
        ]

    def test_resume(self):
        doc = self._getdoc('    abc')

        root = syntax_highlight.Root()
        keyword = syntax_highlight.Keywords(root, 'keyword', ['abc', 'ghi'])
        root.add_tokens(keyword)

        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 2)

        styles = list(tokeniter)
        assert styles == [
            (0, 4, root.styleid_default), 
            (4, 7, keyword.styleid_token)]

        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 6)

        doc.styles.setints(4, 7, keyword.styleid_token)
        styles = list(tokeniter)
        assert styles == [
            (4, 7, keyword.styleid_token)]


class TestHighlight_Nest(kaa_testutils._TestDocBase):
    def test_nest_resume(self):

        doc = self._getdoc('   abc   123')

        root = syntax_highlight.Root()

        sub = syntax_highlight.Tokenizer(root, None)
        keyword2 = syntax_highlight.Keywords(sub, 'keyword', ['123'])
        sub.add_tokens(keyword2)

        class SubKeyword(syntax_highlight.Keywords):
            def on_start(self, doc, match, end):
                pos = yield from super().on_start(doc, match, end)
                return (yield from sub.run(doc, pos, end))

        keyword = SubKeyword(root, 'keyword', ['abc'])
        root.add_tokens(keyword)

        doc.styles.setints(0, 3, root.styleid_default)
        doc.styles.setints(3, 6, keyword.styleid_token)
        doc.styles.setints(6, 9, sub.styleid_default)
        doc.styles.setints(9, 12, keyword2.styleid_token)

        # parse at blank
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 2)

        styles = list(tokeniter)
        assert styles == [
            (0, 3, root.styleid_default),
            (3, 6, keyword.styleid_token),
            (6, 9, sub.styleid_default),
            (9, 12, keyword2.styleid_token)]


        # parse at first token
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 4)

        styles = list(tokeniter)
        assert styles == [
            (3, 6, keyword.styleid_token),
            (6, 9, sub.styleid_default),
            (9, 12, keyword2.styleid_token)]

        # parse at blank of sub2
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 8)

        styles = list(tokeniter)
        assert styles == [
            (6, 9, sub.styleid_default),
            (9, 12, keyword2.styleid_token)]


        # parse at blank of keyword2
        tokeniter = syntax_highlight.begin_tokenizer(
            doc, root, 0, doc.endpos(), 11)

        styles = list(tokeniter)
        assert styles == [
            (9, 12, keyword2.styleid_token)]

