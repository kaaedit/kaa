from kaa.filetype import filetypedef


class FileTypeInfo(filetypedef.FileTypeInfo):
    FILE_EXT = {'.md'}

    @classmethod
    def get_modetype(cls):
        from kaa.filetype.markdown.markdownmode import MarkdownMode
        return MarkdownMode
