import os

FILE_EXT = {'.css'}

def get_modetype(filename):
    from kaa.filetype.css.cssmode import CSSMode
    return CSSMode

