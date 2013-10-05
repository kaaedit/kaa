from contextlib import ExitStack
from unittest.mock import patch

import kaa
from kaa.ui.framelist import framelistmode
import kaa_testutils

class _frame:
    def get_title(self):
        return 'title'

class TestFrameList(kaa_testutils._TestDocBase):

    @patch('kaa.app', create=True)
    def test_framelist(self, mock1):
        kaa.app.DEFAULT_THEME = 'default'
        with ExitStack() as st:
            frames = [_frame(), _frame()]
            st.enter_context(patch('kaa.app.get_frames',
                            create=True, return_value=frames))
            st.enter_context(patch('kaa.app.get_activeframe',
                            create=True, return_value=frames[0]))

            doc = framelistmode.FrameListMode.build()

