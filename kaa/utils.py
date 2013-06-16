import os

def split_existing_dirs(path):
    path, p = os.path.split(path)
    rights = [p]
    while True:
        if not path or os.path.isdir(path):
            if rights:
                rest = os.path.join(*rights)
            else:
                rest = ''
            return path, rest
        path, right = os.path.split(path)
        if right:
            rights.insert(0, right)
