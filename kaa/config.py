import sys

class Config:
    FILETYPES = [
        'kaa.filetype.python',
        'kaa.filetype.html',
        'kaa.filetype.javascript',
        'kaa.filetype.css',
    ]

    NEWLINES = ['auto', 'dos', 'unix']
    DEFAULT_NEWLINE = 'auto'

    NEWLINE_CHARS = {
        'auto': None,
        'dos': '\r\n',
        'unix': '\n'
    }

    DEFAULT_ENCODING = 'utf-8'

