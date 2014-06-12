from kaa import screen, document
import kaa_testutils


class TestTranslateChars:

    def test_transform(self):
        chrs, cols, positions, intervals = screen.translate_chars(
            10, 'abcdefg', 8, 2)

        assert chrs == 'abcdefg'
        assert cols == [1] * 7
        assert positions == list(range(10, 17))
        assert intervals == [0] * 7

    def test_tab(self):
        chrs, cols, positions, intervals = screen.translate_chars(
            10, 'ab\t\tc', 4, 2)

        assert chrs == 'ab      c'
        assert cols == [1] * 9
        assert positions == [10, 11, 12, 12, 13, 13, 13, 13, 14]
        assert intervals == [0, 0, 0, 1, 0, 1, 2, 3, 0]

    def test_ctrlchars(self):
        chrs, cols, positions, intervals = screen.translate_chars(
            10, '\x01\x02\x03\x7f', 8, 2)

        assert chrs == r'\x01\x02\x03\x7f'
        assert cols == [1] * 16
        assert positions == [
            10, 10, 10, 10, 11, 11, 11, 11,
            12, 12, 12, 12, 13, 13, 13, 13]
        assert intervals == [0, 1, 2, 3] * 4

        chrs, cols, positions, intervals = screen.translate_chars(
            10, '\r\n', 8, 2)

        assert chrs == '\\r\n'
        assert cols == [1] * 3
        assert positions == [10, 10, 11]
        assert intervals == [0, 1, 0]


class TestColumnSplitter:

    def test_split(self):
        rows = screen.col_splitter(
            6, 0, '0123456789', [1] * 10, list(range(10)), [0] * 10, [0] * 10, {})

        row1, row2 = rows
        assert row1.chars == '01234'
        assert row1.cols == [1, 1, 1, 1, 1]
        assert row1.positions == [0, 1, 2, 3, 4]
        assert row1.posfrom == 0
        assert row1.posto == 5

        assert row2.chars == '56789'
        assert row2.cols == [1, 1, 1, 1, 1]
        assert row2.positions == [5, 6, 7, 8, 9]
        assert row2.posfrom == 5
        assert row2.posto == 10

    def test_empty(self):
        rows = screen.col_splitter(5, 0, [], [], [], [], [], {})

        row, = rows
        assert row.chars == []
        assert row.cols == []
        assert row.positions == []
        assert row.posfrom == 0
        assert row.posto == 0

    def test_newline(self):
        rows = screen.col_splitter(
            5, 0, '0123\n', [1] * 5, list(range(5)), [1] * 5, [0] * 5, {})

        row, = rows
        assert row.chars == '0123\n'
        assert row.cols == [1, 1, 1, 1, 1]
        assert row.positions == [0, 1, 2, 3, 4]
        assert row.posfrom == 0
        assert row.posto == 5

    def test_controlchr(self):
        chrs, cols, positions, intervals = screen.translate_chars(
            0, '\x01\x02\x03\x7f', 8, 2)
        rows = screen.col_splitter(
            6, 0, chrs, cols, positions, intervals, [0] * 4, {})

        row1, row2, row3, row4 = rows
        assert row1.chars == '\\x01\\'
        assert row2.chars == 'x02\\x'
        assert row3.chars == '03\\x7'
        assert row4.chars == 'f'

    def test_nowrap(self):
        class C:
            nowrap = True

        rows = screen.col_splitter(4, 0, '0123456789', [1] * 10,
                                   list(range(10)), [0] * 10,
                                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0], {1: C})

        row1, row2, row3, row4 = rows
        assert row1.chars == '01'
        assert row2.chars == '234'
        assert row3.chars == '567'
        assert row4.chars == '89'

        rows = screen.col_splitter(3, 0, '0123456789', [1] * 10,
                                   list(range(10)), [0] * 10,
                                   [1, 1, 1, 1, 1, 0, 0, 0, 0, 0], {1: C})

        row1, row2, row3, row4, row5 = rows
        assert row1.chars == '01'
        assert row2.chars == '23'
        assert row3.chars == '45'
        assert row4.chars == '67'
        assert row5.chars == '89'

        rows = screen.col_splitter(3, 0, '0123456789', [1] * 10,
                                   list(range(10)), [0] * 10,
                                   [0, 0, 1, 1, 1, 0, 0, 0, 0, 0], {1: C})

        row1, row2, row3, row4, row5 = rows
        assert row1.chars == '01'
        assert row2.chars == '23'
        assert row3.chars == '45'
        assert row4.chars == '67'
        assert row5.chars == '89'

    def test_combine(self):
        rows = screen.col_splitter(
            3, 0, '0\u0300\u0300\u0300\u0300\u0300\u030012',
            [1, 0, 0, 0, 0, 0, 0, 1, 1], list(range(9)), [0] * 9, [0] * 9, {})

        row1, row2 = rows
        assert row1.chars == '0\u0300\u0300\u0300\u0300\u0300\u03001'
        assert row1.cols == [1, 0, 0, 0, 0, 0, 0, 1]
        assert row1.positions == [0, 1, 2, 3, 4, 5, 6, 7]
        assert row1.posfrom == 0
        assert row1.posto == 8

        assert row2.chars == '2'
        assert row2.cols == [1]
        assert row2.positions == [8]
        assert row2.posfrom == 8
        assert row2.posto == 9


class TestScreen(kaa_testutils._TestScreenBase):

    def test_build(self):
        scrn = self._getscreen("abc")

        row, = scrn.get_visible_rows()
        assert row.posfrom == 0
        assert row.posto == 3

    def test_nowrap(self):
        scrn = self._getscreen("abcdefg\n1234567890", width=3, nowrap=True)

        row1, row2 = scrn.get_visible_rows()
        assert row1.posfrom == 0
        assert row1.posto == 8

        assert row2.posfrom == 8
        assert row2.posto == 18

    def test_wrapindent(self):
        scrn = self._getscreen('    ' + '0123456789' * 16, width=80)
        row1, row2, row3 = scrn.get_visible_rows()
        assert row1.posfrom == 0
        assert row1.posto == 79

        assert row2.posfrom == 79
        assert row2.posto == 154

        assert row3.posfrom == 154
        assert row3.posto == 164

    def test_getrow(self):
        scrn = self._getscreen("abcdefghi", width=4, height=1)
        scrn.locate(6, top=True)

        idx, row = scrn.getrow(6)
        assert idx == 2
        assert row.posfrom == 6
        assert row.posto == 9

        idx, row = scrn.getrow(9)
        assert idx == 2
        assert row.posfrom == 6
        assert row.posto == 9

        scrn = self._getscreen("1\n2\n3\n", width=3, height=2)
        scrn.locate(4, top=True)

        idx, row = scrn.getrow(0)
        assert idx == -1
        assert row is None

        scrn = self._getscreen("1\n2\n3\n4\n4\n5\n6\n7\n", width=3, height=2)
        scrn.locate(4, top=True)

        idx, row = scrn.getrow(10)
        assert idx == -1
        assert row is None

        scrn = self._getscreen("abcdefghi\n", width=4, height=2)
        scrn.locate(6, top=True)

        idx, row = scrn.getrow(9)
        assert idx == 2
        assert row.posfrom == 6
        assert row.posto == 10

        idx, row = scrn.getrow(10)
        assert idx == 3
        assert row.posfrom == 10
        assert row.posto == 10

    def test_get_pos_under(self):
        scrn = self._getscreen("\u3042\u3043\u3044\n")
        assert scrn.get_pos_under(0, 3) == 1
        assert scrn.get_pos_under(1, 3) == 4
        assert scrn.get_pos_under(0, 100) == 3

        scrn = self._getscreen("0123456789", width=4)
        assert scrn.get_pos_under(1, 3) == 5
        assert scrn.get_pos_under(1, 10) == 5
        assert scrn.get_pos_under(3, 2) == 10

        scrn = self._getscreen("\t", width=4)
        assert scrn.get_pos_under(1, 0) == 1

        scrn = self._getscreen("\t\n", width=4)
        assert scrn.get_pos_under(1, 0) == 1
        assert scrn.get_pos_under(1, 10) == 1

    def test_get_pos_above(self):
        scrn = self._getscreen("\u3042\u3043\u3044\n")
        assert scrn.get_pos_above(0, 3) == 1
        assert scrn.get_pos_under(1, 3) == 4
        assert scrn.get_pos_under(0, 100) == 3

        scrn = self._getscreen("0123456789", width=4)
        assert scrn.get_pos_above(1, 3) == 5
        assert scrn.get_pos_above(1, 10) == 5
        assert scrn.get_pos_above(3, 2) == 10

        scrn = self._getscreen("\t\t", width=4)
        assert scrn.get_pos_above(1, 0) == 0

        scrn = self._getscreen("\t\t", width=3)
        assert scrn.get_pos_above(1, 0) == 0

    def test_getpos_fromrowcol(self):
        return
        scrn = self._getscreen("\u3042\u3043\u3044\n")
        assert scrn.getpos_fromrowcol(0, 3) == 1
        assert scrn.getpos_fromrowcol(1, 3) == 4
        assert scrn.getpos_fromrowcol(0, 100) == 3

        scrn = self._getscreen("0123456789", width=4)
        assert scrn.getpos_fromrowcol(1, 3) == 5
        assert scrn.getpos_fromrowcol(3, 2) == 10

        scrn = self._getscreen("\t\t\t\t", width=10)
        assert scrn.getpos_fromrowcol(0, 0) == 0
        assert scrn.getpos_fromrowcol(0, 1) == 0
        assert scrn.getpos_fromrowcol(0, 2) == 0
        assert scrn.getpos_fromrowcol(0, 3) == 0
        assert scrn.getpos_fromrowcol(0, 4) == 1
        assert scrn.getpos_fromrowcol(0, 5) == 1
        assert scrn.getpos_fromrowcol(0, 6) == 1
        assert scrn.getpos_fromrowcol(0, 7) == 1
        assert scrn.getpos_fromrowcol(0, 8) == 2
        assert scrn.getpos_fromrowcol(0, 9) == 2

        assert scrn.getpos_fromrowcol(1, 0) == 2
        assert scrn.getpos_fromrowcol(1, 1) == 2
        assert scrn.getpos_fromrowcol(1, 2) == 2
        assert scrn.getpos_fromrowcol(1, 3) == 3
        assert scrn.getpos_fromrowcol(1, 4) == 3

        scrn = self._getscreen('\t' * 2 + '01234567890', width=9)
        assert scrn.getpos_fromrowcol(0, 7) == 1

    def test_get_pos_at_cols(self):
        scrn = self._getscreen("012345\nabcdef", width=4, height=3)
        ret = scrn.get_pos_at_cols(7, 4)
        assert ret == 11

    def test_newline(self):
        scrn = self._getscreen("abc\n")

        row1, row2 = scrn.get_visible_rows()
        assert row1.posfrom == 0
        assert row1.posto == 4

        assert row2.posfrom == 4
        assert row2.posto == 4

        scrn = self._getscreen("abc\ndef", height=1)
        row1, = scrn.get_visible_rows()
        assert row1.posfrom == 0
        assert row1.posto == 4

        assert row2.posfrom == 4
        assert row2.posto == 4

    def test_empty(self):
        scrn = self._getscreen("")

        row, = scrn.get_visible_rows()
        assert row.posfrom == row.posto == 0

    def test_locate_empty(self):
        scrn = self._getscreen("", width=3, height=1)

        scrn.locate(0, top=True)
        assert scrn.portfrom == 0
        assert scrn.portto == 1

        scrn.locate(0, middle=True)
        assert scrn.portfrom == 0
        assert scrn.portto == 1

        scrn.locate(0, bottom=True)
        assert scrn.portfrom == 0
        assert scrn.portto == 1

    def test_locate(self):
        scrn = self._getscreen("012345\nabcdef", width=4, height=3)
        scrn.locate(7, top=True, align_always=True)
        assert scrn.portfrom == 0
        assert scrn.portto == 2
        assert scrn.pos == 7

        row1, row2 = scrn.get_visible_rows()
        assert row1.posfrom == 7
        assert row1.posto == 10

        assert row2.posfrom == 10
        assert row2.posto == 13

        scrn.locate(8, middle=True, align_always=True)
        assert scrn.portfrom == 1
        assert scrn.portto == 4
        assert scrn.pos == 3

        row1, row2, row3 = scrn.get_visible_rows()
        assert row1.posfrom == 3
        assert row1.posto == 7

        assert row2.posfrom == 7
        assert row2.posto == 10

        assert row3.posfrom == 10
        assert row3.posto == 13

        scrn.locate(8, bottom=True, align_always=True)
        assert scrn.portfrom == 0
        assert scrn.portto == 3
        assert scrn.pos == 0

        row1, row2, row3 = scrn.get_visible_rows()
        assert row1.posfrom == 0
        assert row1.posto == 3

        assert row2.posfrom == 3
        assert row2.posto == 7

        assert row3.posfrom == 7
        assert row3.posto == 10

    def test_linedown(self):
        scrn = self._getscreen("", height=1)
        assert scrn.linedown() == False

        scrn = self._getscreen("abc", height=1)
        assert scrn.linedown() == False

        scrn = self._getscreen("abc\n", height=1)
        assert scrn.linedown()

        row, = scrn.get_visible_rows()
        assert scrn.pos == row.posfrom == 4
        assert row.posto == 4

        scrn = self._getscreen("abc\ndef", height=1)
        assert scrn.linedown()

        row, = scrn.get_visible_rows()
        assert scrn.pos == row.posfrom == 4
        assert row.posto == 7

        scrn = self._getscreen("abcdef", width=4, height=1)
        assert scrn.linedown()

        row, = scrn.get_visible_rows()
        assert scrn.pos == row.posfrom == 3
        assert row.posto == 6

    def test_lineup(self):
        scrn = self._getscreen("", height=1)
        assert scrn.lineup() == False

        scrn = self._getscreen("abc\ndef\n", height=1)
        scrn.linedown()
        assert scrn.pos == 4

        assert scrn.lineup()
        assert scrn.pos == 0
        row, = scrn.get_visible_rows()
        assert row.posfrom == 0
        assert row.posto == 4

        scrn = self._getscreen("abcdef", width=3, height=1)
        scrn.linedown()
        assert scrn.pos == 2

        assert scrn.lineup()
        assert scrn.pos == 0
        row, = scrn.get_visible_rows()
        assert row.posfrom == 0
        assert row.posto == 2

    def test_updatescreen(self):
        scrn = self._getscreen("abcdefg\nabcdefg\n", width=4, height=3)
        scrn.locate(3, top=True, refresh=True)

        scrn.document.insert(0, '123')
        scrn.on_document_updated(0, 3, 0)
        scrn.apply_updates()

        assert scrn.pos == 6

        # delete chars of same line of tos row
        scrn.document.delete(0, 3)
        scrn.on_document_updated(0, 0, 3)
        scrn.apply_updates()

        assert scrn.pos == 6

        scrn.locate(8, top=True, refresh=True)

        # delete chars of previous line of tos
        scrn.document.delete(0, 3)
        scrn.on_document_updated(0, 0, 3)
        scrn.apply_updates()

        assert scrn.pos == 5
