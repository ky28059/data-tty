import socket
from threading import Thread


class GameServer(Thread):
    def __init__(self, port: int):
        super().__init__()

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind(("localhost", port))
        print(f"Started server on port {port}")

        self.connections = []

    def handle_conn(self, conn: socket.socket, address):
        while True:
            user_input = conn.recv(1).decode()
            if not user_input:
                break
            print(address, user_input)  # TODO listeners

    def run(self):
        self.server.listen()

        while True:
            (client_socket, address) = self.server.accept()
            print("Received connection: ", client_socket, address)

            conn = Thread(target=self.handle_conn, args=(client_socket, address))
            self.connections.append(conn)
            conn.start()
