import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))

from util.game_server import GameServer
from util.player_conn import PlayerConnection
from util.screen import Screen


class CoordServer(GameServer):
    def __init__(self, port: int):
        super().__init__(port)

        self.messages = []
        self.player_buffers = {}

    def broadcast(self, message):
        self.messages.append(message)
        for conn in self.connections:  # Draw message on all connected screens
            self.draw(conn)

    def on_connect(self, conn):
        self.player_buffers[conn.tty] = ""
        self.broadcast(f"{conn.name} joined the chat")
        print('Received connection from', conn.name)

    def on_resize(self, conn):
        self.draw(conn)  # Redraw window on resize

    def on_disconnect(self, conn):
        print('Lost connection to', conn.name)
        self.broadcast(f"{conn.name} left the chat")
        del self.player_buffers[conn.tty]

    def on_input(self, conn, key: str):
        if ord(key) == 127:
            # Backspace; delete the last character
            self.player_buffers[conn.tty] = self.player_buffers[conn.tty][0:-1]
        elif key == "\n" or key == "\r":
            # Send the message
            self.broadcast(f"[{conn.name}]: {self.player_buffers[conn.tty]}")
            self.player_buffers[conn.tty] = ""
        else:
            self.player_buffers[conn.tty] += key

        # Redraw display with new buffer
        self.draw(conn)

    def update(self):
        pass

    def draw(self, conn: PlayerConnection):
        """
        Draws / updates the terminal display for the given player connection.
        :param conn: The connection to draw to.
        """
        scr = Screen(conn)

        # Draw messages
        y = conn.height - 3
        for msg in reversed(self.messages):
            if y <= -1:
                break

            scr.write_text(msg, 0, y)
            y -= 1

        # Draw textbox
        scr.write_text('> ', 0, -1)
        scr.write_text(self.player_buffers[conn.tty], 2, -1)
        conn.write(scr.to_bytes())


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003

    server = CoordServer(port)
    server.start()
