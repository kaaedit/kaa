from contextlib import ExitStack
from unittest.mock import patch

import kaa
import kaa_testutils


class TestSwitchSource(kaa_testutils._TestScreenBase):

    def test_switchsource(self):
        with ExitStack() as st:
            ec = st.enter_context

            wnd = self._getwnd('')
            ec(patch.object(wnd, 'show_doc', create=True))

            frame = kaa_testutils.DmyFrame()
            frame.docs = [wnd.document]

            ec(patch('kaa.app.get_frames',
                     create=True, return_value=[frame]))

            def show_dlg(doc):
                doc.mode.callback(False)
            ec(patch('kaa.app.show_dialog', new=show_dlg, create=True))

            kaa.app.app_commands.editor_switchfile(wnd)

            args, kwargs = wnd.show_doc.call_args
            assert args[0] is wnd.document


class TestJoinWindow(kaa_testutils._TestScreenBase):

    def test_joinwindow(self):
        with ExitStack() as st:
            ec = st.enter_context

            wnd = self._getwnd('')
            ec(patch.object(wnd, 'splitter', create=True))
            ec(patch.object(kaa.app, 'get_activeframe', create=True))
            ec(patch.object(wnd, 'show_doc', create=True))

            kaa.app.app_commands.editor_joinwindow(wnd)

            args, kwargs = wnd.splitter.parent.join.call_args
            assert args[0] is wnd
