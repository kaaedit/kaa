import sys
import os
KAA_VERSION = (0, 54, 0)


def version_info():
    return '''\
Kaa {major}.{minor}.{micro}
Copyright (c) 2013 - 2023 Atsuo Ishimoto.
All Rights Reserved.

Python version: {python_version}
Platform: {platform}
$TERM: {term}
'''.format(
        major=KAA_VERSION[0], minor=KAA_VERSION[1],
        micro=KAA_VERSION[2],
        python_version=sys.version,
        platform=sys.platform,
        term=repr(os.environ.get('TERM', ''))[1:-1])
