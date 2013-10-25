from contextlib import ExitStack
from unittest.mock import patch

import kaa
from kaa.ui.framelist import framelistmode
import kaa_testutils

class _frame:
    def get_title(self):
        return 'title'

@patch('kaa.app', new=kaa_testutils.DmyApp(), create=True)
class TestFrameList(kaa_testutils._TestDocBase):

    def test_framelist(self):
        with ExitStack() as st:
            frames = [_frame(), _frame()]
            st.enter_context(patch('kaa.app.get_frames',
                            create=True, return_value=frames))
            st.enter_context(patch('kaa.app.get_activeframe',
                            create=True, return_value=frames[0]))

            doc = framelistmode.FrameListMode.build()

