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

def getch():
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
        conn.send(b'\x04' + int.to_bytes(ord(ch), 1, "little"))
    conn.close()

def handle_resize():
    size = os.get_terminal_size()
    print(f"Terminal resized to {size.columns}x{size.lines}")
    conn.send(b'\x02' + struct.pack("<I", size.columns) + struct.pack("<I", size.lines))

signal.signal(signal.SIGWINCH, handle_resize)
handle_resize()

input_thread = threading.Thread(target=get_input, daemon=True)
input_thread.start()

while True:
    c = conn.recv(1)
    if not c:
        print("Closed")
        break

input_thread.join(0.1)
