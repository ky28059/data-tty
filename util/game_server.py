import socket
import time
from threading import Thread
from typing import Callable, Any


class GameServer(Thread):
    def __init__(
        self,
        port: int,
        on_connect: Callable[[Any], None],
        on_input: Callable[[Any, str], None],
    ):
        super().__init__()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", port))
        print(f"Started server on port {port}")

        # Save listeners
        self.on_connect = on_connect
        self.on_input = on_input

        # Server threads
        self.accept_thread = None
        self.connections = []

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

    def run(self):
        # Handle connections in another thread
        self.accept_thread = Thread(target=self.wait_for_conns, daemon=True)
        self.accept_thread.start()

        # Run game loop
        while True:
            # TODO: game loop

            time.sleep(0.1)
