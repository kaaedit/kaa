import kaa_testutils
from kaa.filetype.default import defaultmode, modebase


class TestDefaultMode(kaa_testutils._TestScreenBase):
    def test_getwords(self):
        mode = self._getmode()
        doc = self._getdoc('0123   \tabc ::::あいうえおカキクケコ[[')
        doc.setmode(mode)

        assert (
            (0, 4, '0123'),
            (4, 8, '   \t'),
            (8, 11, 'abc'),
            (11, 12, ' '),
            (12, 16, '::::'),
            (16, 21, 'あいうえお'),
            (21, 26, 'カキクケコ'),
            (26, 28, '[[')) == tuple(mode.split_word(0))

        mode = self._getmode()
        doc = self._getdoc('\n\n')
        doc.setmode(mode)

        assert (
            (0, 1, '\n'),
        ) == tuple(mode.split_word(0))

    def test_search_next(self):
        w = self._getwnd('abcdefgabcdefg/efg/EFG')

        opt = defaultmode.SearchOption()
        opt.text = 'EFG'
        opt.ignorecase = True
        opt.word = False
        opt.regex = False

        ret = w.document.mode.search_next(w, 0, opt)
        assert ret == (4, 7)

        opt.word = True
        ret = w.document.mode.search_next(w, 0, opt)
        assert ret == (15, 18)

        opt.ignorecase = False
        ret = w.document.mode.search_next(w, 0, opt)
        assert ret == (19, 22)

        opt.text = r'[EFG]+'
        opt.regex = True
        ret = w.document.mode.search_next(w, 0, opt)
        assert ret == (19, 22)

        opt.text = r'[EFG]+'
        opt.regex = False
        ret = w.document.mode.search_next(w, 0, opt)
        assert ret is None


    def test_search_next(self):
        w = self._getwnd('abcdefgabcdefg/efg/EFG01234567890')

        opt = modebase.SearchOption()
        opt.text = 'EFG'
        opt.ignorecase = True
        opt.word = False
        opt.regex = False

        endpos = w.document.endpos()
        ret = w.document.mode.search_prev(w, endpos, opt)
        assert ret == (19, 22)

        opt.text = r'[EFG]+'
        opt.regex = False
        ret = w.document.mode.search_prev(w, endpos, opt)
        assert ret is None


    def test_iter_parenthsis(self):
        doc = self._getdoc("({[]})")
        doc.styles.replaceints(0, doc.endpos(), [1,2,3,4,5,6])

        ret =[(pos, c, attr) for pos, c, attr in doc.mode.iter_parenthesis(0)]

        assert ret == [(0,'(',1), (1,'{',2), (2,'[',3),
                (3,']',4), (4,'}',5), (5,')',6)]

    def test_iter_rev_parenthsis(self):
        doc = self._getdoc("({[]})")
        doc.styles.replaceints(0, doc.endpos(), [1,2,3,4,5,6])

        ret =[(pos, c, attr) for pos, c, attr in doc.mode.iter_rev_parenthesis(5)]

        assert ret == [(5,')',6), (4,'}',5), (3,']',4),
                       (2,'[',3), (1,'{',2), (0,'(',1)]

    def test_find_pair_parenthesis(self):
        doc = self._getdoc("({[({[]})]})")
        doc.styles.replaceints(0, doc.endpos(), [1,1,1,2,2,2,2,2,2,1,1,1])

        assert doc.mode.find_match_parenthesis(0) == 11