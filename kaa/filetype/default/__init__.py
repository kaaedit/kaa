from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.default.defaultmode import DefaultMode
        return DefaultMode
