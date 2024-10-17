import sys
from pathlib import Path

from util.player_conn import PlayerConnection

sys.path.append(str(Path(__file__).parent.parent.parent))

from util.game_server import GameServer


class CoordServer(GameServer):
    def __init__(self, port: int):
        super().__init__(port)

        self.player_coords = {}

    def on_connect(self, conn):
        print('Received connection from', conn.name)
        conn.write(b'hiii\n')

        self.player_coords[conn.tty] = [0, 0]

    def on_disconnect(self, conn):
        print('Lost connection to', conn.name)
        del self.player_coords[conn.tty]

    def on_resize(self, conn: PlayerConnection):
        pass

    def on_input(self, conn, key: str):
        print(conn.width, conn.height, key)
        match key:
            case "a":
                self.player_coords[conn.tty][0] -= 1
            case "d":
                self.player_coords[conn.tty][0] += 1
            case "w":
                self.player_coords[conn.tty][1] -= 1
            case "s":
                self.player_coords[conn.tty][1] += 1

    def update(self):
        for conn in self.connections:
            x, y = self.player_coords[conn.tty]
            conn.write(f"\x1b[2Kx: {x} y: {y}\r".encode())


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003

    server = CoordServer(port)
    server.start()
