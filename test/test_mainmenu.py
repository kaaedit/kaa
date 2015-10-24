from unittest.mock import patch, Mock

import kaa
from kaa.ui.mainmenu import menumode
import kaa_testutils

kaa.app.show_dialog = Mock()


class TestMenuMode(kaa_testutils._TestDocBase):

    def test_msbbox(self):
        kaa.app.DEFAULT_THEME = 'basic'

        target = kaa_testutils._TestScreenBase()._getwnd('')
        doc = menumode.MenuMode.show_menu(target, 'MAIN')
        doc.mode.on_str(None, 'f')

        name, args, kwargs = kaa.app.show_dialog.mock_calls[-1]
        assert args[0].mode.itemname == 'FILE'
