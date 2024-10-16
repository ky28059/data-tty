import socket
import struct
import subprocess
import sys
import termios
import tty

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.connect(("localhost", int(sys.argv[1])))


id = int(subprocess.run(['tty'], stdout=subprocess.PIPE).stdout[9:-1].decode())
server.send(b'\x01' + struct.pack("<i", id))

def getch():
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

while True:
    try:
        ch = getch()
        server.send(b'\x04' + struct.pack("B", ord(ch)))
        if ord(ch) == 3 in [3, 4, 28]:
            break
    except KeyboardInterrupt:
        print("killed")
        break
