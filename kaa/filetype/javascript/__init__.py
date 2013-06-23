import os

FILE_EXT = {'.js'}

def get_modetype(filename):
    from kaa.filetype.javascript.javascriptmode import JavaScriptMode
    return JavaScriptMode

