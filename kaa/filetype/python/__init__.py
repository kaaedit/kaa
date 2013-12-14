from kaa.filetype import filetypedef

class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.py', '.pyw'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.python.pythonmode import PythonMode
        return PythonMode

    @classmethod
    def update_fileinfo(cls, fileinfo):
        import tokenize
        try:
            buffer = open(fileinfo.fullpathname, 'rb')
            encoding, lines = tokenize.detect_encoding(buffer.readline)
            fileinfo.encoding = encoding
        except IOError:
            pass

