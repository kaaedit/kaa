from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.py', '.pyw'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.python.pythonmode import PythonMode
        return PythonMode
