import os
import random
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

code_open = True
code = random.randint(0, 999999)
code_proc = subprocess.Popen(
    f"python3 -c 'import time;while(True):time.sleep(1)#{str(code).zfill(6)}'",
    stdin=subprocess.PIPE,
    stdout=subprocess.PIPE,
    stderr=subprocess.PIPE,
    shell=True
)

conn.send(b'\x01' + struct.pack("<I", id) + struct.pack("<I", code))

stdin = sys.stdin.fileno()
old_stdin = termios.tcgetattr(stdin)
tty.setraw(stdin)

def get_input():
    global code_open
    while True:
        ch = sys.stdin.read(1)
        if ord(ch) == 3 in [3, 4, 28]:
            break
        if ord(ch) > 255:
            continue
        conn.send(b'\x04' + int.to_bytes(ord(ch), 1, "little"))

        # if the connection didn't fail we can wipe the code
        if code_open:
            code_proc.kill()
            code_open = False
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
            print("Connection closed")
            break
    except:
        break

input_thread.join(0.1)
# Revert
termios.tcsetattr(sys.stdin.fileno(), termios.TCSADRAIN, old_stdin)
