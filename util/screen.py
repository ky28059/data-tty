from util.player_conn import PlayerConnection


class Screen:
    def __init__(self, conn: PlayerConnection):
        self.width = conn.width
        self.height = conn.height
        self.chars = []
        for _ in range(self.height):
            self.chars.append(bytearray([b"\n"] * self.width))

    def to_bytes(self):
        out = b""
        for arr in self.chars:
            out += b"".join(arr)
        return out
