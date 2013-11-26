import sys
import os
import socket
import kaadbg.debug

def run_file():
    filename = sys.argv[0]
    # Replace pdb's dir with script's dir in front of module search path.
    sys.path[0] = os.path.dirname(filename)

    kaadbg.debug.port = kaadbg.debug.Kdb()
    kaadbg.debug.port.sock = socket.fromfd(
                int(os.environ['KAADBG_PORT']), 
                socket.AF_UNIX, socket.SOCK_STREAM)

    kaadbg.debug.port.exec_file(filename)

if __name__ == "__main__":
    # Run the module specified as the next command line argument
    if len(sys.argv) < 2:
        exit("No module specified for execution")
    else:
        del sys.argv[0]
        run_file()

