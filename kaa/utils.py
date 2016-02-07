import kaa
import os
import functools


def ignore_errors(f):
    @functools.wraps(f)
    def wrapper(*args, **kwargs):
        try:
            return f(*args, **kwargs)
        except Exception:
            try:
                kaa.log.exception('')
            except Exception:
                # Ignore error completely...
                pass

    return wrapper


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


def shorten_filename(f):
    rel = os.path.relpath(f)
    home = os.path.join('~', os.path.relpath(f, os.path.expanduser('~')))

    tp = sorted(((n.count(os.sep), len(n), n) for n in (f, rel, home)))
    return tp[0][2]
