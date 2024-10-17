import abc
import socket
import time
from threading import Thread

from util.player_conn import PlayerConnection


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

            conn = PlayerConnection(
                client_socket,
                on_connect=self.add_player,
                on_disconnect=self.remove_player,
                on_resize=self.on_resize,
                on_input=self.on_input
            )
            conn.start()

    def start(self):
        # Handle connections in another thread
        self.accept_thread = Thread(target=self.wait_for_conns, daemon=True)
        self.accept_thread.start()

        # Run game loop
        while True:
            self.update()
            time.sleep(self.tick_rate)

    def add_player(self, conn: PlayerConnection):
        self.connections.append(conn)
        self.on_connect(conn)

    def remove_player(self, conn: PlayerConnection):
        self.connections.remove(conn)
        self.on_disconnect(conn)

    @abc.abstractmethod
    def on_connect(self, conn: PlayerConnection):
        pass

    @abc.abstractmethod
    def on_disconnect(self, conn: PlayerConnection):
        pass

    @abc.abstractmethod
    def on_resize(self, conn: PlayerConnection):
        pass

    @abc.abstractmethod
    def on_input(self, conn: PlayerConnection, user_input: str):
        pass

    @abc.abstractmethod
    def update(self):
        pass
