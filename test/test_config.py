import os
from kaa import config


class TestHistory:

    def test_history(self):
        storage = config.KaaHistoryStorage('')
        try:
            hist = storage.get_history('hist1')
            hist.add('1', 1)
            hist.add('2', 2)
            hist.add('1', 1)

            assert hist.get() == [('1', 1), ('2', 2)]
            assert hist.find('1') == 1

            storage.flush()
            assert hist.get() == [('1', 1), ('2', 2)]
            assert hist.find('1') == 1

            hist.add('1', 1)
            hist.add('3', 3)
            assert hist.get() == [('3', 3), ('1', 1), ('2', 2), ]

            storage.flush()
            assert hist.get() == [('3', 3), ('1', 1), ('2', 2), ]

        finally:
            storage.close()

    def test_histclose(self):
        storage = config.KaaHistoryStorage('test.db')
        try:
            hist = storage.get_history('hist2')

            for i in range(config.History.MAX_HISTORY * 3):
                hist.add(str(i))
        finally:
            storage.flush()
            storage.close()

        storage = config.KaaHistoryStorage('test.db')
        try:
            hist = storage.get_history('hist2')

            assert len(hist.get()) == config.History.MAX_HISTORY
            hist.close()
        finally:
            storage.close()
            os.unlink('test.db')
