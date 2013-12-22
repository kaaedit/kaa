from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.htm', '.html'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.html.htmlmode import HTMLMode
        return HTMLMode
