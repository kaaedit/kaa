import os

class FileTypeInfo:
    FILE_EXT = {}

    @classmethod
    def select_mode(cls, fileinfo):
        ext = os.path.splitext(fileinfo.filename)[1].lower()
        if ext in cls.FILE_EXT:
            return cls.get_modetype()

    @classmethod
    def get_modetype(cls):
        assert 0

    @classmethod
    def update_fileinfo(cls, fileinfo):
        pass