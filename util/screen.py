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
        if x < 0:
            x += self.width
        if y < 0:
            y += self.height
        self.lines[y][x:len(text)+x] = text.encode()

    def horizontal_line(self, y: int, x_start: int = 0, x_end: int = None, char = b"-"):
        if x_end is None:
            x_end = self.width
        if x_start < 0:
            x_start += self.width
        if x_end < 0:
            x_end += self.width
        if y < 0:
            y += self.height

        self.lines[y][x_start:x_end+1] = char * (x_end - x_start + 1)

    def vertical_line(self, x: int, y_start: int = 0, y_end: int = None, char = b"-"):
        if y_start is None:
            y_start = 0
        if y_end is None:
            y_end = self.height
        if x < 0:
            x += self.width
        if y_start < 0:
            y_start += self.height
        if y_end < 0:
            y_end += self.height

        for y in range(y_start, y_end):
            self.lines[y][x] = ord(char)

    def fill_rect(self, x_start: int, y_start: int, x_end: int, y_end: int, char = b"-"):
        if x_start < 0:
            x_start += self.width
        if x_end < 0:
            x_end += self.width
        if y_start < 0:
            y_start += self.height
        if y_end < 0:
            y_end += self.height
        for y in range(y_start, y_end+1):
            self.lines[y][x_start:x_end+1] = char * (x_end-x_start + 1)
