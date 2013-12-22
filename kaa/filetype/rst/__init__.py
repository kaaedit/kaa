from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.rst'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.rst.rstmode import RstMode
        return RstMode
