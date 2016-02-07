import argparse


def build_parser():
    parser = argparse.ArgumentParser(description='kaa text editor.')

    parser.add_argument('--version', dest='show_version', action='store_true',
                        default=False, help='show version info and exit')

    parser.add_argument('--no-init', dest='no_init', action='store_true',
                        default=False, help='skip loading initialization script')

    parser.add_argument('--init-script', dest='init_script',
                        help='execute file as initialization script'
                        'instead of default initialization file')

    parser.add_argument('--palette', dest='palette', default=None,
                        help='color palette. available values: dark, light.')

    parser.add_argument('--term', '-t', dest='term', default='',
                        help='specify terminal type')

    parser.add_argument('--command', '-x', dest='command', default='',
                        help='spefify kaa command id to execute on start up.'
                        'e.g: kaa -x python.console / kaa -x tools.grep')

    parser.add_argument('file', nargs='*', default=[])

    return parser
