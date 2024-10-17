import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent.parent))

from util.game_server import GameServer
from util.player_conn import PlayerConnection

ESC = b"\x1b"

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
        self.broadcast(f"{conn.name} joined the chat")
        print('Received connection from', conn.name)

        self.player_buffers[conn.tty] = ""

    def on_disconnect(self, conn):
        print('Lost connection to', conn.name)
        del self.player_buffers[conn.tty]

    def on_input(self, conn, key: str):
        if key == "\n":
            # send the message
            self.broadcast(f"[{conn.name}]: {self.player_buffers[conn.tty]}")
            self.player_buffers[conn.tty] = ""
        else:
            self.player_buffers[conn.tty] += key
            self.draw(conn)

    def update(self):
        pass

    def draw(self, conn: PlayerConnection):
        conn.write(b"\f")
        conn.write(ESC + b"[2J") # Erase

        # Draw textbox
        conn.write(ESC + f"[{conn.height - 1};0f".encode())
        conn.write(self.player_buffers[conn.tty].encode())

        # Draw messages
        y = conn.height - 3
        for msg in self.messages.__reversed__():
            conn.write(ESC + f"[{y};0f".encode())
            conn.write(msg.encode())
            y -= 1
            if y == -1:
                break



if __name__ == '__main__':
    port = 5003
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    server = CoordServer(port)
    server.start()
