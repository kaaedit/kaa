FILE_EXT = {'.diff', '.patch'}

def get_modetype():
    from kaa.filetype.diff.diffmode import DiffMode
    return DiffMode

