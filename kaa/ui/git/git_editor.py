import os
import socket
sockname = os.environ['KAA_SOCKNAME']

s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
s.connect(sockname)
s.send(b'ok\n')
s.recv(4096)
s.close()
