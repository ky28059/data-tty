import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from util.game_server import GameServer
from util.player_conn import PlayerConnection
from util.term import erase, go_to


class CoordServer(GameServer):
    def __init__(self, port: int):
        super().__init__(port)

        self.messages = []
        self.player_buffers = {}

    def broadcast(self, message):
        self.messages.append(message)
        for conn in self.connections:
            self.draw(conn)

    def on_connect(self, conn):
        self.player_buffers[conn.tty] = ""
        self.broadcast(f"{conn.name} joined the chat")
        print('Received connection from', conn.name)

    def on_resize(self, conn):
        self.draw(conn)

    def on_disconnect(self, conn):
        print('Lost connection to', conn.name)
        del self.player_buffers[conn.tty]

    def on_input(self, conn, key: str):
        print(ord(key))
        if ord(key) == 127: # backspace
            self.player_buffers[conn.tty] = self.player_buffers[conn.tty][0:-1]
        elif key == "\n" or key == "\r":
            # send the message
            self.broadcast(f"[{conn.name}]: {self.player_buffers[conn.tty]}")
            self.player_buffers[conn.tty] = ""
        else:
            self.player_buffers[conn.tty] += key
        self.draw(conn)

    def update(self):
        pass

    def draw(self, conn: PlayerConnection):
        erase(conn)

        # Draw messages
        y = conn.height - 3
        for msg in self.messages.__reversed__():
            go_to(conn, 0, y)
            conn.write(msg.encode())
            y -= 1
            if y == -1:
                break

        # Draw textbox
        go_to(conn, 0, -1)
        conn.write(self.player_buffers[conn.tty].encode())


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003

    server = CoordServer(port)
    server.start()
