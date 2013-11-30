import sys
import os
import socket
import kaadbg.debug
import re


def run_file(portno):
    filename = sys.argv[0]
    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(filename)

    kaadbg.debug.port = kaadbg.debug.Kdb()

    port = os.environ.get('KAADBG_DOMAINPORT')
    if portno is None and not port:
        portno = kaadbg.debug.DEFAULT_PORT_NO

    if portno:
        kaadbg.debug.port.connect(portno)
    else:
        kaadbg.debug.port.sock = socket.fromfd(
            int(port),
            socket.AF_UNIX, socket.SOCK_STREAM)

    kaadbg.debug.port.exec_file(filename)


def usage():
    print('''python -m kaadbg.run [-p portno] myscript.py myarg1 myargs''')


def _args():
    if len(sys.argv) == 2:
        if sys.argv[1] == '-h':
            usage()
            exit(0)

    del sys.argv[0]

    m = re.match(r'-p(\d+)?', sys.argv[0])
    if m:
        del sys.argv[0]
        no = m.group(1)
        if no:
            no = int(no)
        else:
            no = int(sys.argv[0])
            del sys.argv[0]
    else:
        no = None

    return no

if __name__ == "__main__":
    try:
        portno = _args()
    except Exception:
        usage()
        sys.exit(1)

    if not sys.argv:
        usage()
        sys.exit(1)

    run_file(portno)
