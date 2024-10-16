import socket
import struct
from threading import Thread
from typing import Callable, Self

from tty import tty_write


class PlayerConnection(Thread):
    def __init__(
        self,
        client_socket: socket.socket,
        on_input: Callable[[Self, str], None]
    ):
        super().__init__(daemon=True)

        self.socket = client_socket
        self.tty = None

        self.width = 80
        self.height = 25

        self._on_input = on_input

    def process_packet(self):
        packet_type = self.socket.recv(1)
        if not packet_type:
            raise Exception('No packet received')

        match packet_type:
            case b'\x01':  # id packet
                raise Exception("Disallowed tty packet")

            case b'\x02':  # resize packet
                self.width = self.get_int()
                self.height = self.get_int()
                print(f"New window: {self.width}, {self.height}")

            case b'\x04':  # char input
                c = self.socket.recv(1).decode()
                self._on_input(self, c)

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

        # Continuously read and process user input
        while True:
            self.process_packet()

    def write(self, data: bytes):
        tty_write(self.tty, data)

    def get_int(self):
        self.socket.settimeout(1)
        value = struct.unpack("<i", self.socket.recv(4))
        self.socket.settimeout(None)
        return value[0]
