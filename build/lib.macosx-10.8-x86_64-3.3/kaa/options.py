import argparse

def build_parser():
    parser = argparse.ArgumentParser(description='kaa text editor.')
    parser.add_argument('file', help='edit file', nargs='*', default=[])

    return parser
