import socket
from threading import Thread


class GameClient(Thread):
    def __init__(self, port: int):
        super().__init__()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.connect(("localhost", port))
        # print(f"Connected to server on port {port}")
