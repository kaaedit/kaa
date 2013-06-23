import os

FILE_EXT = {'.htm', '.html'}

def get_modetype(filename):
    from kaa.filetype.html.htmlmode import HTMLMode
    return HTMLMode

