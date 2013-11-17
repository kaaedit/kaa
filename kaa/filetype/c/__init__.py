FILE_EXT = {'.h', '.c'}

def get_modetype():
    from kaa.filetype.c.cmode import CMode
    return CMode

