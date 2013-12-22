from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.h', '.c'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.c.cmode import CMode
        return CMode
