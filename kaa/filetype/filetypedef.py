import os


class FileTypeInfo:
    FILE_EXT = {}

    @classmethod
    def select_mode(cls, filename):
        ext = os.path.splitext(filename)[1].lower()
        if ext in cls.FILE_EXT:
            return cls.get_modetype()

    @classmethod
    def get_modetype(cls):
        assert 0
