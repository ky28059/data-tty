from util.player_conn import PlayerConnection

ESC = b"\x1b"

def erase(conn: PlayerConnection):
    conn.write(ESC + b"[2J")

def go_to(conn: PlayerConnection, x: int, y: int):
    if x < 0:
        x = conn.width + x + 1
    if y < 0:
        y = conn.height + y + 1
    conn.write(ESC + f"[{y};{x}f".encode())
