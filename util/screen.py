from util.player_conn import PlayerConnection


class Screen:
    def __init__(self, conn: PlayerConnection):
        self.width = conn.width
        self.height = conn.height
        self.lines = []
        for i in range(self.height):
            self.lines.append(bytearray(b' ' * self.width))

    def to_bytes(self):
        out = b""
        for arr in self.lines:
            out += bytes(arr) + b'\n'
        return out

    def write_text(self, text: str, x: int, y: int):
        self.lines[y][x:len(text)+x] = text.encode()

    def horizontal_line(self, y: int, x_start: int = 0, x_end: int = None, char = b"-"):
        if x_end is None:
            x_end = self.width

        self.lines[y][x_start:x_end] = char * (x_end - x_start)

    def vertical_line(self, x: int, y_start: int = 0, y_end: int = None, char = b"-"):
        if y_start is None:
            y_start = 0
        if y_end is None:
            y_end = self.height

        for y in range(y_start, y_end):
            self.lines[y][x] = char
