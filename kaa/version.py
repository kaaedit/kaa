import sys
KAA_VERSION = (0, 0, 4)

def version_info():
    return '''\
Kaa {major}.{minor}.{micro}
Copyright (c) 2013 Atsuo Ishimoto.
All Rights Reserved.

Python version: {python_version}
Platform: {platform}
'''.format(
    major=KAA_VERSION[0], minor=KAA_VERSION[1],
    micro=KAA_VERSION[2],
    python_version=sys.version,
    platform=sys.platform)