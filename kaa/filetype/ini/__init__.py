from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.ini'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.ini.inimode import INIMode
        return INIMode
