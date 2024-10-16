from util.game_server import GameServer


class CoordServer(GameServer):
    def __init__(self):
        super().__init__(5003)

        self.player_coords = {}

    def on_connect(self, conn):
        print('Received connection from', conn.tty)
        conn.write(b'hiii\n')

        self.player_coords[conn.tty] = [0, 0]

    def on_input(self, conn, key: str):
        print(conn.width, conn.height, key)
        match key:
            case b"a":
                self.player_coords[conn.tty][0] -= 1
            case b"d":
                self.player_coords[conn.tty][0] += 1
            case b"w":
                self.player_coords[conn.tty][1] -= 1
            case b"s":
                self.player_coords[conn.tty][1] += 1

    def update(self):
        for conn in self.connections:
            x, y = self.player_coords[conn.tty]
            conn.write(f"\x1b[2Kx: {x} y: {y}\r".encode())


if __name__ == '__main__':
    server = CoordServer()
    server.start()
