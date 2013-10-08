import argparse

def build_parser():
    parser = argparse.ArgumentParser(description='kaa text editor.')

    parser.add_argument('--version', dest='show_version', action='store_true', 
            default=False, help='show version info and exit')
    parser.add_argument('file', nargs='*', default=[])

    return parser
