from unittest.mock import patch

import kaa
from kaa.ui.msgbox import msgboxmode
import kaa_testutils


class TestSearchDlgMode(kaa_testutils._TestDocBase):

    def test_msgbox(self):
        kaa.app.DEFAULT_THEME = 'basic'

        def cb(c):
            pass
        doc = msgboxmode.MsgBoxMode.show_msgbox(
            'caption', ['&Yes', '&No', '&All', '&Cancel'], cb)

        assert doc.mode.shortcuts == {
            'y': '&Yes', 'n': '&No', 'a': '&All', 'c': '&Cancel'
        }
