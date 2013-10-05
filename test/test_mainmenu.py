from unittest.mock import patch

import kaa
from kaa.ui.mainmenu import mainmenumode
import kaa_testutils

class TestMenuMode(kaa_testutils._TestDocBase):

    @patch('kaa.app', create=True)
    def test_msbbox(self, mock):
        kaa.app.DEFAULT_THEME = 'default'

        target = kaa_testutils._TestScreenBase()._getwnd('')
        doc = mainmenumode.MenuMode.build_menu(target,
                               [('&File', ('testmenu',)),
                                ('&edit', ('menu.edit',)),])

        value = 0
        def f(wnd):
            nonlocal value
            value = 'updated'
        target.document.mode.commands['testmenu'] = f
        doc.mode.on_str(kaa_testutils._TestScreenBase()._getwnd(''), 'f')

        assert value == 'updated'
