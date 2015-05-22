from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.json'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.json.jsonmode import JSONMode
        return JSONMode
