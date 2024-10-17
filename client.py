import os
import signal
import socket
import struct
import subprocess
import sys
import termios
import threading
import tty

conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
conn.connect(("localhost", int(sys.argv[1])))


id = int(subprocess.run(['tty'], stdout=subprocess.PIPE).stdout[9:-1].decode())
conn.send(b'\x01' + struct.pack("<I", id))

old = None

def getch():
    global old
    fd = sys.stdin.fileno()
    old = termios.tcgetattr(fd)
    try:
        tty.setraw(fd)
        return sys.stdin.read(1)
    finally:
        termios.tcsetattr(fd, termios.TCSADRAIN, old)

def get_input():
    while True:
        ch = getch()
        if ord(ch) == 3 in [3, 4, 28]:
            break
        if ord(ch) > 255:
            continue
        conn.send(b'\x04' + int.to_bytes(ord(ch), 1, "little"))
    conn.shutdown(socket.SHUT_RDWR)
    conn.close()

def send_window_dimensions(*_):
    size = os.get_terminal_size()
    conn.send(b'\x02' + struct.pack("<I", size.columns) + struct.pack("<I", size.lines))

signal.signal(signal.SIGWINCH, send_window_dimensions)
send_window_dimensions()

input_thread = threading.Thread(target=get_input, daemon=True)
input_thread.start()

while True:
    try:
        c = conn.recv(1)
        if not c:
            print("Closed")
            break
    except:
        break

input_thread.join(0.1)
# Revert
termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old)
