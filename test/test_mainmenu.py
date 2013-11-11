from unittest.mock import patch

import kaa
from kaa.ui.mainmenu import menumode
import kaa_testutils

class TestMenuMode(kaa_testutils._TestDocBase):

    @patch('kaa.app', create=True)
    def test_msbbox(self, mock):
        kaa.app.DEFAULT_THEME = 'basic'

        target = kaa_testutils._TestScreenBase()._getwnd('')
        doc = menumode.MenuMode.show_menu(target, 'MAIN')
        doc.mode.on_str(None, 'f')

        name, args, kwargs = kaa.app.show_dialog.mock_calls[-1]
        assert args[0].mode.itemname == 'FILE'
        