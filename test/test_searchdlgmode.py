from unittest.mock import patch

import kaa
from kaa.ui.searchdlg import searchdlgmode
import kaa_testutils

class TestSearchDlgMode(kaa_testutils._TestDocBase):

    def _getmodeclass(self):
        return lambda :searchdlgmode.SearchDlgMode(
            target=kaa_testutils._TestScreenBase()._getwnd(''))

    @patch('kaa.app', create=True)
    def test_searchdlg(self, mock):
        doc = self._getdoc('')
        doc.mode.option.text = ''

        doc.mode.build_document()
        ignorecase = doc.mode.option.ignorecase
        word = doc.mode.option.word
        regex = doc.mode.option.regex

        doc.mode.toggle_option_ignorecase(None)
        doc.mode.toggle_option_word(None)
        doc.mode.toggle_option_regex(None)

        assert ignorecase != doc.mode.option.ignorecase
        assert word != doc.mode.option.word
        assert regex != doc.mode.option.regex

        pos = doc.marks['searchtext']
        doc.insert(pos[0], 'test string')

        assert doc.mode.get_search_str() == 'test string'

    @patch('kaa.app', create=True)
    def test_execsearh(self, mock):
        doc = self._getdoc('')
        doc.mode.build_document()

        option = doc.mode.option
        option.ignorecase = False
        option.word = False
        option.regex = False
        pos = doc.marks['searchtext']
        doc.insert(pos[0], 'test string')

        doc.mode.target.document.append('012345test string')
        doc.mode.search_next(None)
        assert doc.mode.target.screen.selection.get_selrange() == (6, 17)


class TestReplaceDlg(kaa_testutils._TestDocBase):

    def _getmodeclass(self):
        return lambda :searchdlgmode.ReplaceDlgMode(
            target=kaa_testutils._TestScreenBase()._getwnd(''))

    @patch('kaa.app', create=True)
    def test_replacedlg(self, mock):

        doc = self._getdoc('')
        doc.mode.option.text = ''
        doc.mode.build_document()

        ignorecase = doc.mode.option.ignorecase
        word = doc.mode.option.word
        regex = doc.mode.option.regex

        doc.mode.toggle_option_ignorecase(None)
        doc.mode.toggle_option_word(None)
        doc.mode.toggle_option_regex(None)

        assert ignorecase != doc.mode.option.ignorecase
        assert word != doc.mode.option.word
        assert regex != doc.mode.option.regex

        pos = doc.marks['searchtext']
        doc.insert(pos[0], 'test string')

        assert doc.mode.get_search_str() == 'test string'

    @patch('kaa.app', create=True)
    def test_execsearh(self, mock):
        kaa.app.DEFAULT_THEME = 'basic'

        doc = self._getdoc('')
        doc.mode.option.text = ''
        doc.mode.build_document()

        option = doc.mode.option
        option.ignorecase = False
        option.word = False
        option.regex = False
        pos = doc.marks['searchtext']
        doc.insert(pos[0], 'test string')

        doc.mode.target.document.append('012345test string')
        doc.mode.search_next(None)
        assert doc.mode.target.screen.selection.get_selrange() == (6, 17)

