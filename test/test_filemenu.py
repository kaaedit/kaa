from contextlib import ExitStack
from unittest.mock import patch

import kaa
import kaa_testutils


class TestSaveAll(kaa_testutils._TestScreenBase):

    def test_saveall(self):
        with ExitStack() as st:
            ec = st.enter_context

            wnd = self._getwnd('')
            ec(patch.object(wnd.document.undo, 'is_dirty', return_value=True))

            frame = kaa_testutils.DmyFrame()
            ec(patch.object(frame, 'get_editors',
               create=True, return_value=[wnd]))

            mainframe = ec(patch.object(wnd, 'mainframe', create=True))
            mainframe.childframes = [frame]

            ec(patch.object(kaa.app, 'storage', create=True))
            ec(patch.object(kaa.app, 'get_activeframe', create=True,
                            return_value=frame))

            ec(patch.object(wnd.document.undo, 'is_dirty', return_value=True))
            ec(patch.object(wnd.document,
               'get_filename', return_value='filename'))

            kaa.app.file_commands.file_saveall(wnd)

            args, kwargs = kaa.app.storage.save_document.call_args
            assert args[0] is wnd.document
