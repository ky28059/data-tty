from util.game_server import GameServer


class TestServer(GameServer):
    def __init__(self):
        super().__init__(5003)

    def on_connect(self, conn):
        print('Received connection from', conn.tty)

    def on_input(self, conn, user_input: str):
        print(conn.width, conn.height, user_input)

    def update(self):
        pass


if __name__ == '__main__':
    server = TestServer()
    server.start()
