import socket
import time
from threading import Thread
import abc


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

    def handle_conn(self, conn: socket.socket, address):
        self.on_connect(address)

        # Continuously read and process user input
        while True:
            user_input = conn.recv(1).decode()
            if not user_input:
                break  # TODO?
            self.on_input(address, user_input)

    def wait_for_conns(self):
        self.server.listen()

        while True:
            (client_socket, address) = self.server.accept()
            print("Received connection: ", client_socket, address)

            conn = Thread(target=self.handle_conn, args=(client_socket, address), daemon=True)
            self.connections.append(conn)
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
    def on_connect(self, address):
        pass

    @abc.abstractmethod
    def on_input(self, address, user_input: str):
        pass

    @abc.abstractmethod
    def update(self):
        pass
