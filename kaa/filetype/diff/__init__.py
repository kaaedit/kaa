from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.diff', '.patch'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.diff.diffmode import DiffMode
        return DiffMode
