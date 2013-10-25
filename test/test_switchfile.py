from contextlib import ExitStack
from unittest.mock import patch

import kaa
import kaa_testutils

class _frame:
    def get_title(self):
        return 'title'
        
    def get_documents(self):
        return self.docs
        
@patch('kaa.app', new=kaa_testutils.DmyApp(), create=True)
class TestSwitchSource(kaa_testutils._TestScreenBase):

    def test_switchsource(self):
        with ExitStack() as st:
            ec = st.enter_context
            
            wnd = self._getwnd('')
            ec(patch.object(wnd, 'show_doc', create=True))
            
            frame = _frame()
            frame.docs = [wnd.document]

            ec(patch('kaa.app.get_frames',
                            create=True, return_value=[frame]))

            def show_dlg(doc):
                doc.mode.callback(False)
            ec(patch('kaa.app.show_dialog', new=show_dlg, create=True))
            
            wnd.document.mode.app_commands.editor_switchfile(wnd)

            args, kwargs = wnd.show_doc.call_args
            assert args[0] is wnd.document