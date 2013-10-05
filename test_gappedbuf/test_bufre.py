import pytest
import _gappedbuf
import gappedbuf.re

class TestGappedBuf:

    def test_match(self):
        regex = gappedbuf.re.compile('.*')

        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, 'abcdefg')
        
        assert regex.match(buf).group() == 'abcdefg'
        assert regex.match(buf, 1, 5).group() == 'bcde'
    
        # move gap
        buf.insert(0, '0123456789')
        assert regex.match(buf).group() == '0123456789abcdefg'
        assert regex.match(buf, 1, 15).group() == '123456789abcde'

    def test_search(self):

        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, 'abcdefg0123456789')
        buf.insert(10, 'あいうえお')
        regex = gappedbuf.re.compile('[あ-お]+')
        assert regex.search(buf, 11).group() == 'いうえお'

    def test_empty(self):
        buf = _gappedbuf.GappedBuffer()
        regex = gappedbuf.re.compile('abc', gappedbuf.re.IGNORECASE)
        assert regex.search(buf, 0) is None

    def test_finditer(self):
        class B(_gappedbuf.GappedBuffer):
            pass

        buf = _gappedbuf.GappedBuffer()
        buf = B()
        buf.insert(0, '0123 abc あいうえお')

        RE_SPLITWORD = gappedbuf.re.compile('.')

        assert ''.join(m.group() for m in RE_SPLITWORD.finditer(buf, 0)) == '0123 abc あいうえお'

    def test_group(self):
        buf = _gappedbuf.GappedBuffer()
        buf.insert(0, 'a')
        regex = gappedbuf.re.compile(r'(a)')
        assert regex.search(buf, 0).group(1) == 'a'

