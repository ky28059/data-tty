import socket
import struct
from threading import Thread
from typing import Any, Callable

from util.tty import tty_close, tty_to_fd, tty_write


class PlayerConnection(Thread):
    def __init__(
        self,
        client_socket: socket.socket,
        on_connect: Callable[[Any], None],  # TODO: "self"
        on_disconnect: Callable[[Any], None],  # TODO: "self"
        on_input: Callable[[Any, str], None],
    ):
        super().__init__(daemon=True)

        self.socket = client_socket
        self.tty = None
        self.name = None

        self.width = 80
        self.height = 25

        # Private listeners inherited from the server
        self._on_connect = on_connect
        self._on_disconnect = on_disconnect
        self._on_input = on_input

    def process_packet(self):
        packet_type = self.socket.recv(1)
        if not packet_type:
            raise Exception('No packet received')

        match packet_type:
            case b'\x01':  # tty/name packet
                raise Exception("Disallowed tty packet")

            case b'\x02':  # resize packet
                self.width = self.get_int()
                self.height = self.get_int()

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

        tty_id = self.get_int()
        self.tty = tty_to_fd(tty_id)

        self.name = self.get_str().decode("utf-8")

        # Once initialized, call `on_connect()`
        self._on_connect(self)

        # Continuously read and process user input
        while True:
            try:
                self.process_packet()
            except Exception:
                # Stop if disconnected or if error occurs processing packet
                break
        self.close()
        self._on_disconnect(self)


    def write(self, data: bytes):
        tty_write(self.tty, data)

    def get_int(self):
        self.socket.settimeout(1)
        value = struct.unpack("<i", self.socket.recv(4))
        self.socket.settimeout(None)
        return value[0]

    def get_str(self):
        self.socket.settimeout(1)
        length = int.from_bytes(self.socket.recv(1), 1, "little")
        value = self.socket.recv(length)
        self.socket.settimeout(None)
        return value

    def close(self):
        tty_close(self.tty)
        self.socket.shutdown(socket.SHUT_RDWR)
        self.socket.close()
