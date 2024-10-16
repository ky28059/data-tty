from util.game_server import GameServer


class TestServer(GameServer):
    def __init__(self):
        super().__init__(5003)

    def on_connect(self, address):
        print('Connected to server')

    def on_input(self, address, user_input: str):
        print(user_input)

    def update(self):
        pass


if __name__ == '__main__':
    server = TestServer()
    server.start()
