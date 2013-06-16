import os

FILE_EXT = {'.py', '.pyw'}

def get_modetype(filename):
    from kaa.filetype.python.pythonmode import PythonMode
    return PythonMode

