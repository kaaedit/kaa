import kaa_testutils
from kaa import highlight
from kaa.filetype.html import htmlmode
from kaa.filetype.html.htmlmode import get_encoding




class TestEncDecl:

    def test_html5(self):
        assert 'UTF-8' == get_encoding(b'<meta charset="UTF-8">')
        assert 'UTF-8' == get_encoding(b"<meta charset='UTF-8'>")
        assert not get_encoding(b"<meta charset='UTF-8>")

    def test_html(self):
        assert 'UTF-8' == get_encoding(
            b'''<meta http-equiv="Content-type"
            content="text/html;charset=UTF-8">''')

        assert not get_encoding(
            b'''<meta con="text/html;charset=UTF-8">''')

        assert not get_encoding(
            b'''<meta content="text/html;char=UTF-8">''')

    def test_xml(self):
        assert 'UTF-8' == get_encoding(
            b'<?xml version="1.0" encoding="UTF-8"?>')

        assert not get_encoding(
            b'<?xm version="1.0" encoding="UTF-8"?>')

        assert not get_encoding(
            b'<?xml version="1.0" encoding=""?>')
