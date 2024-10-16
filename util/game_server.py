import socket
import time
from threading import Thread
import abc

from .player_conn import PlayerConnection


class GameServer(abc.ABC):
    def __init__(self, port: int, tick_rate: int = 0.1):
        super().__init__()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", port))
        print(f"Started server on port {port}")

        # Server threads
        self.accept_thread = None
        self.connections = []

        self.tick_rate = tick_rate

    def wait_for_conns(self):
        self.server.listen()

        while True:
            (client_socket, address) = self.server.accept()
            print("Received connection: ", client_socket, address)

            conn = PlayerConnection(client_socket, on_connect=self.on_connect, on_input=self.on_input)
            self.connections.append(conn)  # TODO: handle thread exception
            conn.start()

    def start(self):
        # Handle connections in another thread
        self.accept_thread = Thread(target=self.wait_for_conns, daemon=True)
        self.accept_thread.start()

        # Run game loop
        while True:
            self.update()
            time.sleep(self.tick_rate)

    @abc.abstractmethod
    def on_connect(self, conn: PlayerConnection):
        pass

    @abc.abstractmethod
    def on_input(self, conn: PlayerConnection, user_input: str):
        pass

    @abc.abstractmethod
    def update(self):
        pass
