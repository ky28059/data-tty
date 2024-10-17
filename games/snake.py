import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from dataclasses import dataclass
from random import randint

from util.game_server import GameServer
from util.player_conn import PlayerConnection
from util.screen import Screen


@dataclass
class Snake:
    head: list[int, int]
    tail: list[int, int]
    direction: str

MAPSIZE = (100, 100)

class SnakeServer(GameServer):
    def __init__(self, port: int):
        super().__init__(port, tick_rate=0.15)

        self.map = []
        for _ in range(MAPSIZE[1]):
            self.map.append([" "] * MAPSIZE[0])

        self.snakes: dict[int, Snake] = {}


    def on_connect(self, conn):
        self.snakes[conn.tty] = Snake(head=[49, 49], tail=[49,49], direction="u")
        self.map[49][49] = "u"

    def update(self):
        for conn in self.connections:
            snake = self.snakes[conn.tty]
            # Move the head
            self.map[snake.head[1]][snake.head[0]] = snake.direction
            match snake.direction:
                case "u":
                    snake.head[1] -= 1
                case "d":
                    snake.head[1] += 1
                case "l":
                    snake.head[0] -= 1
                case "r":
                    snake.head[0] += 1
            tile = self.map[snake.head[1]][snake.head[0]]
            ate = False
            if tile == "O":
                ate = True
            if tile in ["u", "d", "l", "r", "H"]:
                # kill the snake
                pos = snake.tail
                while snake.tail[0] != snake.head[0] and snake.tail[1] != snake.head[1]:
                    tile = self.map[snake.tail[1]][snake.tail[0]]
                    self.map[snake.tail[1]][snake.tail[0]] = " "
                    match tile:
                        case "u":
                            snake.tail[1] -= 1
                        case "d":
                            snake.tail[1] += 1
                        case "l":
                            snake.tail[0] -= 1
                        case "r":
                            snake.tail[0] += 1
                print("snake died")
                conn.close()
                continue
            self.map[snake.head[1]][snake.head[0]] = "H"

            if not ate:
                # Move the tail
                tile = self.map[snake.tail[1]][snake.tail[0]]
                self.map[snake.tail[1]][snake.tail[0]] = " "
                match tile:
                    case "u":
                        snake.tail[1] -= 1
                    case "d":
                        snake.tail[1] += 1
                    case "l":
                        snake.tail[0] -= 1
                    case "r":
                        snake.tail[0] += 1

        if randint(0, 2) == 1:
            # spawn food
            pos = (randint(0, MAPSIZE[0] - 1), randint(0, MAPSIZE[1] - 1))
            while self.map[pos[1]][pos[0]] != " ":
                pos = (randint(0, MAPSIZE[0] - 1), randint(0, MAPSIZE[1] - 1))
            self.map[pos[1]][pos[0]] = "O"

        # for row in self.map:
        #     print("".join(row))

        for conn in self.connections:
            self.draw(conn)


    def on_resize(self, conn):
        self.draw(conn)  # Redraw window on resize

    def on_disconnect(self, conn):
        print('Lost connection to', conn.name)
        del self.snakes[conn.tty]

    def on_input(self, conn, key: str):
        print(ord(key))
        #27 91 65
        snake = self.snakes[conn.tty]
        match key:
            case "a":
                snake.direction = "l"
            case "d":
                snake.direction = "r"
            case "w":
                snake.direction = "u"
            case "s":
                snake.direction = "d"



    def draw(self, conn: PlayerConnection):
        """
        Draws / updates the terminal display for the given player connection.
        :param conn: The connection to draw to.
        """
        scr = Screen(conn)

        snake = self.snakes[conn.tty]
        camera = snake.head

        x_min_bound = max(scr.width // 2 - camera[0], 0)
        x_max_bound = min(scr.width // 2 + (MAPSIZE[0] - camera[0]), scr.width)

        for y in range(scr.height):
            map_y = camera[1] - scr.height // 2 + y
            map_sx = max(camera[0] - scr.width // 2, 0)
            if map_y == -1 or map_y == MAPSIZE[1]:
                scr.lines[y][x_min_bound:x_max_bound] = b"#" * (x_max_bound-x_min_bound)
            if map_y < 0 or map_y > MAPSIZE[1] - 1:
                continue
            scr.lines[y][x_min_bound:x_max_bound] = bytes("".join(self.map[map_y][map_sx:map_sx+x_max_bound-x_min_bound]), "utf-8")
            if x_min_bound > 0:
                scr.lines[y][x_min_bound-1] = b"#"
            if x_max_bound < scr.width:
                scr.lines[y][x_max_bound+1] = b"#"

        conn.write(scr.to_bytes())


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003

    server = SnakeServer(port)
    server.start()

