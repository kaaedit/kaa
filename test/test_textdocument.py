from kaa import document
import kaa_testutils


class TestDocument(kaa_testutils._TestScreenBase):

    def test_gettol(self):
        assert self._getdoc('').gettol(0) == 0
        assert self._getdoc('0123').gettol(4) == 0
        assert self._getdoc('0123\n').gettol(4) == 0
        assert self._getdoc('012\n').gettol(4) == 4

    def test_geteol(self):
        assert self._getdoc('').geteol(0) == 0
        assert self._getdoc('0123').geteol(0) == 4
        assert self._getdoc('0123\n').geteol(0) == 5
        assert self._getdoc('012\r3').geteol(0) == 5
        assert self._getdoc('012\r\n').geteol(0) == 5
        assert self._getdoc('012\r\n').geteol(3) == 5
        assert self._getdoc('012\r\n').geteol(4) == 5

    def test_getline(self):
        assert self._getdoc('').getline(0) == (0, '')
        assert self._getdoc('abc').getline(0) == (3, 'abc')

        doc = self._getdoc('abc\ndef\n')
        assert doc.getline(0) == (4, 'abc\n')
        assert doc.getline(4) == (8, 'def\n')
        assert doc.getline(8) == (8, '')

        doc = self._getdoc('abc\r\ndef')
        assert doc.getline(0) == (5, 'abc\r\n')
        assert doc.getline(5) == (8, 'def')

    def test_style(self):
        assert len(self._getdoc('').styles) == 0
        assert len(self._getdoc('abcde').styles) == 5

        doc = self._getdoc()
        doc.insert(0, 'abcde')
        assert doc.styles.getints(0, len(doc.styles)) == [0] * 5

        doc.insert(1, 'abcde')
        assert doc.styles.getints(0, len(doc.styles)) == [0] * 10

    def test_getnextpos(self):
        doc = self._getdoc("abc\ndef\nghi\njkl\n")
        for i in range(16):
            assert doc.get_nextpos(i) == i + 1

        doc = self._getdoc("abc")
        assert doc.get_nextpos(1) == 2
        assert doc.get_nextpos(2) == 3
        assert doc.get_nextpos(3) == 3

        doc = self._getdoc("abcdef")
        for i in range(6):
            assert doc.get_nextpos(i) == i + 1
        assert doc.get_nextpos(6) == 6

        doc = self._getdoc("abc\r\n")
        assert doc.get_nextpos(3) == 4

        doc = self._getdoc("a\u1dc0\u1dc0\u1dc0\u1dc0b")

        assert doc.get_nextpos(0) == 5
        assert doc.get_nextpos(4) == 5
        assert doc.get_nextpos(5) == 6
        assert doc.get_nextpos(6) == 6

    def test_getprevpos(self):
        doc = self._getdoc("abc\ndef\nghi\njkl\n")
        for i in range(1, 17):
            assert doc.get_prevpos(i) == i - 1

        doc = self._getdoc("abc",)
        assert doc.get_prevpos(0) == 0
        assert doc.get_prevpos(1) == 0
        assert doc.get_prevpos(2) == 1
        assert doc.get_prevpos(3) == 2

        doc = self._getdoc("abcdef")
        for i in range(1, 6):
            assert doc.get_prevpos(i) == i - 1
        assert doc.get_prevpos(0) == 0

        doc = self._getdoc("abc\r\n")
        assert doc.get_prevpos(5) == 4

        doc = self._getdoc("a\u1dc0\u1dc0\u1dc0\u1dc0b")

        assert doc.get_prevpos(0) == 0
        assert doc.get_prevpos(4) == 0
        assert doc.get_prevpos(5) == 0
        assert doc.get_prevpos(6) == 5


class TestMark(kaa_testutils._TestDocBase):

    def test_mark(self):
        doc = self._getdoc('01234567890123456789')
        doc.marks['mark1'] = 0
        doc.marks['mark2'] = 1

        doc.delete(0, 1)

        assert doc.marks['mark1'] == 0
        assert doc.marks['mark2'] == 0

        doc.marks['mark3'] = 3
        doc.insert(0, 'abc')

        assert doc.marks['mark1'] == 0
        assert doc.marks['mark2'] == 0
        assert doc.marks['mark3'] == 6

        doc.delete(0, 3)

        assert doc.marks['mark1'] == 0
        assert doc.marks['mark2'] == 0
        assert doc.marks['mark3'] == 3

    def test_rangemark(self):
        doc = self._getdoc('')
        doc.marks['mark1'] = (0, 0)
        doc.insert(0, 'abcde')
        assert doc.marks['mark1'] == (0, 5)

        doc = self._getdoc('01234567890123456789')
        doc.marks['mark1'] = (1, 3)
        doc.delete(0, 1)
        assert doc.marks['mark1'] == (0, 2)

        doc = self._getdoc('01234567890123456789')
        doc.marks['mark1'] = (1, 3)
        doc.delete(1, 2)
        assert doc.marks['mark1'] == (1, 2)

        doc = self._getdoc('01234567890123456789')
        doc.marks['mark1'] = (1, 3)
        doc.delete(1, 3)
        assert doc.marks['mark1'] == (1, 1)

        doc = self._getdoc('01234567890123456789')
        doc.marks['mark1'] = (1, 3)
        doc.delete(1, 4)
        assert doc.marks['mark1'] == (1, 1)


class TestUndo:

    def test_undo(self):
        undo = document.Undo()
        assert not undo.can_undo()
        assert not undo.can_redo()

        undo.add('action1', 1, arg=1)
        assert undo.can_undo()
        assert not undo.can_redo()

        undo.add('action2', 2, arg=2)
        undo.add('action3', 3, arg=3)

        (action, args, kwargs), = undo.undo()
        assert action == 'action3'
        assert args == (3,)
        assert kwargs == {'arg': 3}

        assert undo.can_undo()
        assert undo.can_redo()
        assert undo.can_redo()

        (action, args, kwargs), = undo.undo()
        assert action == 'action2'
        assert args == (2,)
        assert kwargs == {'arg': 2}

        assert undo.can_undo()
        assert undo.can_redo()

        (action, args, kwargs), = undo.undo()
        assert action == 'action1'
        assert args == (1,)
        assert kwargs == {'arg': 1}

        assert not undo.can_undo()
        assert undo.can_redo()

        (action, args, kwargs), = undo.redo()
        assert action == 'action1'
        assert args == (1,)
        assert kwargs == {'arg': 1}

        assert undo.can_undo()
        assert undo.can_redo()

        (action, args, kwargs), = undo.redo()
        assert action == 'action2'
        assert args == (2,)
        assert kwargs == {'arg': 2}

        assert undo.can_undo()
        assert undo.can_redo()

        (action, args, kwargs), = undo.redo()
        assert action == 'action3'
        assert args == (3,)
        assert kwargs == {'arg': 3}

        assert undo.can_undo()
        assert not undo.can_redo()

    def test_dirty(self):
        undo = document.Undo()
        assert not undo.is_dirty()

        undo.add('action1')
        assert undo.is_dirty()

        undo.add('action2')
        assert undo.is_dirty()
        undo.saved()
        assert not undo.is_dirty()

        undo.add('action3')
        assert undo.is_dirty()

        for r in undo.undo():
            pass
        assert not undo.is_dirty()

    def test_addundo(self):
        undo = document.Undo()
        assert not undo.can_undo()
        assert not undo.can_redo()

        undo.add('action1')
        undo.add('action2')
        undo.saved()

        assert not undo.is_dirty()

        for r in undo.undo():
            pass
        undo.add('action3')

        assert (('action3', (), {}),) == tuple(undo.undo())
        assert (('action1', (), {}),) == tuple(undo.undo())

        assert (('action1', (), {}),) == tuple(undo.redo())
        assert (('action3', (), {}),) == tuple(undo.redo())

        assert undo.is_dirty()

    def test_group(self):
        undo = document.Undo()

        undo.add('1')
        undo.add('2')
        undo.beginblock()
        undo.add('3')
        undo.add('4')
        undo.beginblock()
        undo.add('5')
        undo.add('6')
        undo.endblock()
        undo.add('7')
        undo.endblock()
        undo.saved()
        undo.add('8')

        assert undo.is_dirty()
        assert (('8', (), {}),) == tuple(undo.undo())
        assert not undo.is_dirty()

        assert (('7', (), {}),
                ('6', (), {}),
                ('5', (), {}),
                ('4', (), {}),
                ('3', (), {}),
                ) == tuple(undo.undo())
        assert undo.is_dirty()

        assert (('2', (), {}),) == tuple(undo.undo())
        assert (('1', (), {}),) == tuple(undo.undo())

        assert (('1', (), {}),) == tuple(undo.redo())
        assert (('2', (), {}),) == tuple(undo.redo())
        assert (('3', (), {}),
                ('4', (), {}),
                ('5', (), {}),
                ('6', (), {}),
                ('7', (), {}),
                ) == tuple(undo.redo())
        assert not undo.is_dirty()
        assert (('8', (), {}),) == tuple(undo.redo())
        assert undo.is_dirty()


class TestLineNo(kaa_testutils._TestScreenBase):

    def test_bisect_left(self):
        lineno = document.LineNo()
        lineno.buf.insertints(0, [0, 1, 2, 3, 4, 5])

        assert lineno.bisect_left(0) == 0
        assert lineno.bisect_left(1) == 1
        assert lineno.bisect_left(5) == 5
        assert lineno.bisect_left(6) == 6
        assert lineno.bisect_left(7) == 6

        lineno = document.LineNo()
        assert lineno.bisect_left(0) == 0

    def test_insert(self):
        lineno = document.LineNo()
        lineno.inserted(0, 'abc')
        assert len(lineno.buf) == 0

        lineno.inserted(0, 'abc\n')
        assert lineno.buf.getints(0, len(lineno.buf)) == [3]

        lineno.inserted(0, 'abc\n')
        assert lineno.buf.getints(0, len(lineno.buf)) == [3, 7]

        lineno.inserted(0, '\na\nab\n')
        assert lineno.buf.getints(0, len(lineno.buf)) == [0, 2, 5, 9, 13]

        lineno.inserted(14, 'a\nb')
        assert lineno.buf.getints(0, len(lineno.buf)) == [0, 2, 5, 9, 13, 15]

    def test_delete(self):
        lineno = document.LineNo()
        lineno.inserted(0, 'abc\n1def\n23ghi\n')

        lineno.deleted(0, 2)
        assert lineno.buf.getints(0, len(lineno.buf)) == [1, 6, 12]

        lineno.deleted(4, 8)
        assert lineno.buf.getints(0, len(lineno.buf)) == [1, 8]

        lineno = document.LineNo()
        lineno.inserted(0, 'abcdefg')

        lineno.deleted(0, 2)
        assert lineno.buf.getints(0, len(lineno.buf)) == []

        lineno = document.LineNo()
        lineno.inserted(0, 'abc')
        lineno.deleted(0, 100)
        assert lineno.buf.getints(0, len(lineno.buf)) == []

        lineno = document.LineNo()
        lineno.inserted(0, 'abcde')
        lineno.deleted(0, 2)
        assert lineno.buf.getints(0, len(lineno.buf)) == []

        lineno = document.LineNo()
        lineno.inserted(0, 'abcde\nfghi')
        lineno.deleted(0, 2)
        assert lineno.buf.getints(0, len(lineno.buf)) == [3]

        lineno = document.LineNo()
        lineno.inserted(0, 'abcde\nfghi')
        lineno.deleted(6, 8)
        assert lineno.buf.getints(0, len(lineno.buf)) == [5]

        lineno = document.LineNo()
        lineno.inserted(0, 'abcde\nfghi')
        lineno.deleted(3, 8)
        assert lineno.buf.getints(0, len(lineno.buf)) == []

        lineno = document.LineNo()
        lineno.inserted(0, 'abc\ndef')
        lineno.deleted(0, 100)
        assert lineno.buf.getints(0, len(lineno.buf)) == []
