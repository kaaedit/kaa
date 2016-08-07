from unittest.mock import patch

import kaa
from kaa.ui.wordcomplete import wordcompletemode
import kaa_testutils


class TestSearchDlgMode(kaa_testutils._TestDocBase):
    def _run(self, s, pos):
        target = kaa_testutils._TestScreenBase()._getwnd(s)
        doc = wordcompletemode.WordCompleteInputMode.build(target)
        return doc.mode._get_target_word(pos)

    def test_wordcomplete(self):
        assert self._run('hello', 0) == (0, 5)
        assert self._run('hello', 5) == (0, 5)
        assert self._run('', 0) == (0, 0)

    def test_punctuation(self):
        assert self._run('self.', 5) == (5, 5)

    def test_punctuation2(self):
        assert self._run('v[', 1) == (0, 1)

