from pathlib import Path
from git import Repo

def open_repo(d):
    cur = Path(d).absolute()
    while not cur.joinpath('.git').is_dir():
        p = cur.parent
        if p == cur:
            raise RuntimeError('Not a git repogitory')
        cur = p

    repo_dir = str(cur)
    repo = Repo(repo_dir)
    return repo