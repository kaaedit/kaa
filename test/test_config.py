import os
from kaa import config

class TestHistory:
    filename = './test.db'
    def test_history(self):
        storage = config.KaaHistoryStorage(self.filename)
        try:
            hist = config.History('test', storage)
            storage.add_history(hist)

            hist.add('1')
            hist.add('2')
            hist.add('1')
            hist.add('2')

            assert hist.get() == [('2', None), ('1', None)]
            hist.close()
        finally:
            storage.close()
            os.unlink(self.filename)

    def test_histclose(self):
        storage = config.KaaHistoryStorage(self.filename)
        try:
            hist = config.History('test', storage)
            storage.add_history(hist)

            for i in range(config.History.MAX_HISTORY*2):
                hist.add(str(i))
            hist.close()
        finally:
            storage.close()

        storage = config.KaaHistoryStorage(self.filename)
        try:
            hist = config.History('test', storage)
            storage.add_history(hist)

            assert len(hist.get()) == config.History.MAX_HISTORY
            hist.close()
        finally:
            storage.close()
            os.unlink(self.filename)

           