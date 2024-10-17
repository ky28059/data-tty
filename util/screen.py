from util.player_conn import PlayerConnection


class Screen:
    def __init__(self, conn: PlayerConnection):
        self.width = conn.width
        self.height = conn.height
        self.lines = []
        for _ in range(self.height):
            self.lines.append(bytearray(b" " * self.width))

    def to_bytes(self):
        out = b""
        for arr in self.lines:
            out += bytes(arr) + b'\n'
        return out

    def write_text(self, text: str, x: int, y: int):
        self.lines[y][x:len(text)+x] = text.encode()
