import pytest
import sys
import _gappedbuf

class TestGappedBuf:
    def test_gappedbuf(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, 'abc')
        
        assert buf[0] == 'a'
        assert buf[1] == 'b'
        assert buf[2] == 'c'

        assert buf.bufsize == 4096
        assert buf.gap == 3
        assert buf.gapsize == 4093
        assert buf.numelems == 3

        buf.insert(0, '123')

        assert buf.bufsize == 4096
        assert buf.gap == 3
        assert buf.gapsize == 4090
        assert buf.numelems == 6
        assert buf[:] == '123abc'

    def test_insert_index_exceeds(self):
        buf = _gappedbuf.GappedBuffer()
        with pytest.raises(ValueError):
            buf.insert(-1, '1')
        with pytest.raises(ValueError):
            buf.insert(1, '1')

    def test_expand(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, '1'*4096)

        assert buf.bufsize == 4096
        assert buf.gap == 4096
        assert buf.gapsize == 0
        assert buf.numelems == 4096

        buf.insert(4096, '1')
        assert buf.bufsize == 5120
        assert buf.gap == 4097
        assert buf.gapsize == 1023
        assert buf.numelems == 4097
        
        assert buf[:] == '1'*4097

    def test_append(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, '1')
        buf.append('2')
        assert buf[:] == '12'

    def test_del(self):
        buf = _gappedbuf.GappedBuffer()
        s = '0123456789'*500
        buf.insert(0, s)
        buf.delete(0, 1)

        assert buf.gap == 0
        assert buf.numelems == 4999
        assert buf.gapsize == buf.bufsize - buf.numelems 
        
        s = s[1:]
        assert buf[:] == s

        # move gap to center
        buf.delete(2500, 2501)
        assert buf.gap == 2500
        assert buf.numelems == 4998
        assert buf.gapsize == buf.bufsize - buf.numelems 
        
        s = s[:2500]+s[2501:]
        assert buf[:] == s

        # delete before gap
        buf.delete(0, 1)
        assert buf.gap == 0
        assert buf.numelems == 4997
        assert buf.gapsize == buf.bufsize - buf.numelems 
        
        s = s[1:]
        assert buf[:] == s

        # delete after gap
        buf.delete(1, 2)
        assert buf.gap == 1
        assert buf.numelems == 4996
        assert buf.gapsize == buf.bufsize - buf.numelems 
        
        s = s[0:1]+s[2:]
        assert buf[:] == s

        # delete all
        buf.delete(0, buf.numelems)
        assert buf.gap == 0
        assert buf.numelems == 0
        assert buf.gapsize == buf.bufsize - buf.numelems 
        
        assert buf[:] == ''

        with pytest.raises(ValueError):
            buf.delete(0, 1)

    def test_shrink(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, '1'*8192)

        buf.delete(0, 8191)
        assert buf.bufsize == 4097
        assert buf.gap == 0
        assert buf.gapsize == 4096
        assert buf.numelems == 1
        assert buf[:] == '1'

    def test_getitem(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, 'abc')
        
        assert buf[0] == 'a'
        assert buf[1] == 'b'
        assert buf[2] == 'c'
        
        assert buf[-3] == 'a'
        assert buf[-2] == 'b'
        assert buf[-1] == 'c'
        
        with pytest.raises(IndexError):
            buf[1:0]
        with pytest.raises(IndexError):
            buf[3]
        with pytest.raises(IndexError):
            buf[-4]

        buf.insert(0, 'abc')  # move gap to center
        assert buf[0] == 'a'
        assert buf[1] == 'b'
        assert buf[2] == 'c'
        assert buf[3] == 'a'
        assert buf[4] == 'b'
        assert buf[5] == 'c'
        
    def _test_slice(self, s):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, s*2)
        assert buf[:] == s*2

        buf.insert(len(s), s)
        assert buf.gap == len(s)*2
        
        assert buf[:] == s*3
        assert buf[:3] == s[:3]
        assert buf[-3:] == s[-3:]

        buf.delete(len(s)*3-1, len(buf))

        assert len(buf) == len(s)*3-1
        assert buf.gap == len(buf)

        assert buf[:] == (s*3)[:-1]
        assert buf[:3] == s[:3]
        assert buf[-3:] == s[-4:-1]


    def test_getslice(self):
        # test UCS1
        s = 'abcdefghij'
        self._test_slice(s)

        # test UCS2
        s = 'あいうえおかきくけこ'
        self._test_slice(s)

        # test UCS4
        s = ''.join(chr(c) for c in range(0x100000, 0x10000a))
        self._test_slice(s)

        buf = _gappedbuf.GappedBuffer()
        buf[:] = 'abcdefg'
        with pytest.raises(IndexError):
            buf[7]
            
    def test_setitem(self):
        buf = _gappedbuf.GappedBuffer()
        buf[:] = 'abcdefg'
        assert buf[:] == 'abcdefg'

        buf[-1] = 'x'
        assert buf[:] == 'abcdefx'
        
        buf[1] = 'x'
        assert buf[:] == 'axcdefx'

        with pytest.raises(IndexError):
            buf[7] = 'a'
        with pytest.raises(ValueError):
            buf[0] = ''
        with pytest.raises(ValueError):
            buf[0] = '12'
        
    def test_delitem(self):
        buf = _gappedbuf.GappedBuffer()
        buf[:] = 'abcdefg'
        del buf[1:-1]
        assert buf[:] == 'ag'

    def test_findchr(self):
        buf = _gappedbuf.GappedBuffer()
        buf[:] = 'abcdefg'
        buf.insert(0, '0123456789')

        assert buf.findchr("0", 0, 17) == 0
        assert buf.findchr("9", 0, 17) == 9
        assert buf.findchr("a", 0, 17) == 10
        assert buf.findchr("g", 0, 17) == 16
        assert buf.findchr("Ag", 0, 17) == 16
        assert buf.findchr("A", 0, 17) == -1

        with pytest.raises(ValueError):
            buf.findchr('0', 0, 100)

    def test_rfindchr(self):
        buf = _gappedbuf.GappedBuffer()
        buf[:] = 'abcdefg'
        buf.insert(0, '0123456789')

        assert buf.rfindchr("g", 0, 17) == 16
        assert buf.rfindchr("a", 0, 17) == 10
        assert buf.rfindchr("9", 0, 17) == 9
        assert buf.rfindchr("0", 0, 17) == 0
        assert buf.rfindchr("Ag", 0, 17) == 16
        assert buf.rfindchr("A", 0, 17) == -1

        with pytest.raises(ValueError):
            buf.rfindchr('0', 0, 100)

    def test_getints(self):
        buf = _gappedbuf.GappedBuffer()
        buf[:] = 'abcdefg'
        buf.insert(0, '0123456789')

        assert buf.getints(0, 0) == []
        assert buf.getints(0, 1) == [ord('0')]
        assert buf.getints(0, 17) == [ord(c) for c in '0123456789abcdefg']

        n = sys.getrefcount(ord('0'))
        for i in range(100000):
            buf.getints(0, 17) 

        with pytest.raises(ValueError):
            buf.getints(100, 0)

    def test_insertint(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insertints(0, (0,1,2,3,4,5,6,7,8,9))

        assert buf.getints(0, 10) == [0,1,2,3,4,5,6,7,8,9]

        assert buf.bufsize == 4096
        assert buf.gap == 10
        assert buf.gapsize == 4086
        assert buf.numelems == 10

        with pytest.raises(ValueError):
            buf.insertints(11, (0,1,2,3,4,5,6,7,8,9))

    def test_appendint(self):
        buf = _gappedbuf.GappedBuffer()
        buf.appendints((0,1,2,3,4,5,6,7,8,9))

        assert buf.getints(0, 10) == [0,1,2,3,4,5,6,7,8,9]

    def test_replaceints(self):
        buf = _gappedbuf.GappedBuffer()
        buf.appendints((0,1,2,3,4,5,6,7,8,9))
        buf.replaceints(1, 9, (0,1,2,3,4,5,6,7,8,9))

        assert buf.getints(0, 12) == [0,0,1,2,3,4,5,6,7,8,9,9]

    def test_setints(self):
        buf = _gappedbuf.GappedBuffer()
        buf.appendints((0,1,2,3,4,5,6,7,8,9))
        buf.setints(1, 9, 255)

        assert buf.getints(0, 10) == [0,255,255,255,255,255,255,255,255,9]

        with pytest.raises(ValueError):
            buf.setints(0, 11, 255)

    def test_findint(self):
        buf = _gappedbuf.GappedBuffer()
        buf.appendints((0,1,2,3,4,5,6,7,8,9))
        buf.insertints(0, (100,101,102,103,104,105,106,107,108,109))

        assert buf.findint([100, 200], 0, 20, False) == 0
        assert buf.findint([200, 109], 0, 20, False) == 9
        assert buf.findint([0, 20], 0, 20, False) == 10
        assert buf.findint([20, 9], 0, 20, False) == 19
        assert buf.findint([20, 21], 0, 20, False) == -1

        with pytest.raises(ValueError):
            buf.findint([20, 21], 0, 21, False)

    def test_findint_ne(self):
        buf = _gappedbuf.GappedBuffer()

        buf.appendints((0,)*10+(1,))
        assert buf.findint([0], 0, 11, True) == 10

        buf.insertints(0, (0,)*10)
        assert buf.findint([0], 0, 21, True) == 20

        buf.insertints(0, (1,)*10)
        assert buf.findint([0], 0, 21, True) == 0

        buf.insertints(0, (1,)*10)
        assert buf.findint([0, 1], 0, 21, True) == -1


    def test_rfindint(self):
        buf = _gappedbuf.GappedBuffer()
        buf.appendints((0,1,2,3,4,5,6,7,8,9))
        buf.insertints(0, (100,101,102,103,104,105,106,107,108,109))

        assert buf.rfindint([100, 200], 0, 20, False) == 0
        assert buf.rfindint([200, 109], 0, 20, False) == 9
        assert buf.rfindint([0, 200], 0, 20, False) == 10
        assert buf.rfindint([200, 9], 0, 20, False) == 19

        with pytest.raises(ValueError):
            buf.rfindint([20, 21], 0, 21, False)

    def test_rfindint_ne(self):
        buf = _gappedbuf.GappedBuffer()

        buf.appendints((0,)*10+(1,))
        assert buf.rfindint([0, 2], 0, 11, True) == 10

        buf.insertints(0, (0,)*10)
        assert buf.rfindint([2, 0], 0, 21, True) == 20

        buf.insertints(0, (1,)*10)
        assert buf.rfindint([0,2,3], 0, 21, True) == 9

        buf.insertints(0, (1,)*10)
        assert buf.rfindint([0,1], 0, 21, True) == -1

