import socket
import struct
import subprocess
import traceback
from pathlib import Path
from threading import Thread
from typing import Any, Callable


class PlayerConnection(Thread):
    def __init__(
        self,
        client_socket: socket.socket,
        on_connect: Callable[[Any], None],  # TODO: "self"
        on_disconnect: Callable[[Any], None],
        on_resize: Callable[[Any], None],
        on_input: Callable[[Any, str], None],
    ):
        super().__init__(daemon=True)

        self.socket = client_socket
        self.tty = None
        self.name = None
        self.closed = False

        self.width = 80
        self.height = 25

        # Private listeners inherited from the server
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_input = on_input
        self._on_resize = on_resize

    def process_packet(self):
        packet_type = self.socket.recv(1)
        if not packet_type:
            raise Exception('No packet received')

        match packet_type:
            case b'\x01':  # tty packet
                raise Exception("Disallowed tty packet")

            case b'\x02':  # resize packet
                self.width = self.get_int()
                self.height = self.get_int() - 1
                try:
                    self._on_resize(self)
                except:
                    print(traceback.format_exc())

            case b'\x04':  # char input
                c = self.socket.recv(1).decode()
                try:
                    self._on_input(self, c)
                except:
                    print(traceback.format_exc())

            case _:
                raise Exception(f"Invalid packet type {ord(packet_type)}")

    def run(self):
        # Parse header containing TTY info
        # TODO: abstraction
        self.socket.settimeout(1)
        packet_type = self.socket.recv(1)
        if packet_type != b'\x01':
            raise Exception(f"Missing tty packet {packet_type}")
        self.socket.settimeout(None)

        self.tty = self.get_int()
        self.name = Path(f"/dev/pts/{self.tty}").owner()

        self.write_proc = subprocess.Popen(
            f"write {self.name} /dev/pts/{self.tty}",
            stdin=subprocess.PIPE,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            shell=True
        )

        # Once initialized, call `on_connect()`
        try:
            self._on_connect(self)
        except:
            print(traceback.format_exc())

        # Continuously read and process user input
        while True:
            try:
                self.process_packet()
            except Exception as e:
                # Stop if disconnected or if error occurs processing packet
                break
        self.close()


    def write(self, data: bytes):
        self.write_proc.stdin.write(data)
        self.write_proc.stdin.flush()

    def get_int(self):
        self.socket.settimeout(1)
        value = struct.unpack("<i", self.socket.recv(4))
        self.socket.settimeout(None)
        return value[0]

    def get_str(self):
        self.socket.settimeout(1)
        length = int.from_bytes(self.socket.recv(1), "little")
        value = self.socket.recv(length)
        self.socket.settimeout(None)
        return value

    def close(self):
        if self.closed:
            return
        self.closed = True
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
        self.write_proc.stdin.close()
        self.write_proc.terminate()
        try:
            self._on_disconnect(self)
        except:
            print(traceback.format_exc())
