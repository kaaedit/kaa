from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.css'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.css.cssmode import CSSMode
        return CSSMode
