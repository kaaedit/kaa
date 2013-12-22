from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.js'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.javascript.javascriptmode import JavaScriptMode
        return JavaScriptMode
