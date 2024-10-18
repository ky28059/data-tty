import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from dataclasses import dataclass
from random import randint, random

from util.game_server import GameServer
from util.player_conn import PlayerConnection
from util.screen import Screen


@dataclass
class Snake:
    head: list[int, int]
    tail: list[int, int]
    length: int
    direction: str
    stamina: int
    using_stamina: bool
    upd_idx: int

MAPSIZE = (200, 100)
MAX_FOOD = 0.3
FOOD_CONVERSION = 0.4

class SnakeServer(GameServer):
    def __init__(self, port: int):
        super().__init__(port, tick_rate=0.08)

        self.map = []
        self.foodcount = 0
        for _ in range(MAPSIZE[1]):
            self.map.append([" "] * MAPSIZE[0])

        self.snakes: dict[int, Snake] = {}

    def check_spawn(self, point: list[int], radius: int = 2):
        for y in range(point[1]-radius, point[1]+radius+1):
            for x in range(point[0]-radius, point[0]+radius+1):
                if x < 0 or x >= MAPSIZE[0] or y < 0 or y >= MAPSIZE[1]:
                    return False
                if self.map[y][x] != "." and self.map[y][x] != " ":
                    return False
        return True

    def get_spawn(self):
        radius = 15
        while radius > 0:
            for _ in range(5):
                point = [randint(0, MAPSIZE[0] - 1), randint(0, MAPSIZE[1] - 1)]
                if self.check_spawn(point):
                    return point
            radius -= 2
        return None


    def on_connect(self, conn):

        spawn_point = self.get_spawn()
        if not spawn_point:
            conn.write("no suitable spawnpoint found")
            conn.close()

        self.snakes[conn.tty] = Snake(
            head=spawn_point[:],
            tail=spawn_point[:],
            length=1,
            direction="u",
            using_stamina=False,
            stamina=60,
            upd_idx=0,
        )
        self.map[spawn_point[1]][spawn_point[0]] = "u"

    def update(self):
        for conn in self.connections:
            snake = self.snakes[conn.tty]

            # Stamina calc
            snake.upd_idx += 1
            if not snake.using_stamina and snake.upd_idx < 3:
                continue
            if snake.using_stamina and snake.upd_idx < 1:
                continue
            if snake.using_stamina:
                snake.stamina -= 3
            else:
                snake.stamina = min(snake.stamina + 2, 60)
            if snake.stamina <= 0:
                snake.using_stamina = False

            snake.upd_idx = 0

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
            if snake.head[0] < 0 or snake.head[0] >= MAPSIZE[0] or snake.head[1] < 0 or snake.head[1] >= MAPSIZE[1]:
                # out of bounds
                conn.close()
                continue

            tile = self.map[snake.head[1]][snake.head[0]]
            ate = False
            if tile == ".":
                self.foodcount -= 1
                ate = True
            if tile in ["u", "d", "l", "r", "H"]:
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
            else:
                snake.length += 1

        if randint(0, 2) == 1 and self.foodcount < MAPSIZE[0] * MAPSIZE[1] * MAX_FOOD:
            # spawn food
            pos = (randint(0, MAPSIZE[0] - 1), randint(0, MAPSIZE[1] - 1))
            while self.map[pos[1]][pos[0]] != " ":
                pos = (randint(0, MAPSIZE[0] - 1), randint(0, MAPSIZE[1] - 1))
            self.map[pos[1]][pos[0]] = "."
            self.foodcount += 1

        # for row in self.map:
        #     print("".join(row))

        for conn in self.connections:
            self.draw(conn)

    def kill_snake(self, conn):
        if conn.tty not in self.snakes:
            return
        print("snake ", conn.name, " died")
        snake = self.snakes[conn.tty]
        initial_move = True
        while snake.tail[0] != snake.head[0] or snake.tail[1] != snake.head[1] or initial_move:
            initial_move = False
            tile = self.map[snake.tail[1]][snake.tail[0]]
            if random() < FOOD_CONVERSION:
                self.map[snake.tail[1]][snake.tail[0]] = "."
                self.foodcount += 1
            else:
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

    def on_resize(self, conn):
        self.draw(conn)  # Redraw window on resize

    def on_disconnect(self, conn):
        self.kill_snake(conn)
        print('Lost connection to', conn.name)
        del self.snakes[conn.tty]

    def on_input(self, conn, key: str):
        #27 91 65
        snake = self.snakes[conn.tty]
        match key:
            case "a":
                if snake.direction != "r" or snake.length == 1: snake.direction = "l"
            case "d":
                if snake.direction != "l" or snake.length == 1: snake.direction = "r"
            case "w":
                if snake.direction != "d" or snake.length == 1: snake.direction = "u"
            case "s":
                if snake.direction != "u" or snake.length == 1: snake.direction = "d"
            case " ":
                snake.using_stamina = not snake.using_stamina

    def get_snakes_by_length(self):
        j = self.connections[:]
        j.sort(key=lambda x: self.snakes[x.tty].length, reverse=True)
        return j


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
            if x_min_bound > 1:
                scr.lines[y][x_min_bound-1] = ord("#")
            if x_max_bound < scr.width - 1:
                scr.lines[y][x_max_bound] = ord("#")
        sta = f"{snake.stamina}{'T' if snake.using_stamina else 'F'}".encode("utf-8")
        scr.lines[y][:len(sta)] = sta

        # leaderboard

        LEADERBOARD_WIDTH = 20
        LEADERBOARD_HEIGHT = 10
        scr.fill_rect(-LEADERBOARD_WIDTH-1,0,-1,LEADERBOARD_HEIGHT, b" ")
        scr.horizontal_line(0,-LEADERBOARD_WIDTH-1, -1, b"-")
        scr.horizontal_line(LEADERBOARD_HEIGHT,-LEADERBOARD_WIDTH-1, -1, b"-")
        scr.vertical_line(-LEADERBOARD_WIDTH-1, 0, LEADERBOARD_HEIGHT, b"|")
        scr.vertical_line(-1, 0, LEADERBOARD_HEIGHT, b"|")

        l: list[PlayerConnection] = self.get_snakes_by_length()
        position = l.index(conn)

        for y in range(0, LEADERBOARD_HEIGHT - 2):
            pos = position + y -( LEADERBOARD_HEIGHT - 2) // 2
            if pos < 0 or pos >= len(l):
                continue
            scr.write_text(f" {l[pos].name}", -LEADERBOARD_WIDTH + 1, y + 1)
            if pos == position:
                scr.write_text(">", -LEADERBOARD_WIDTH + 1, y + 1)
            lt = str(self.snakes[l[pos].tty].length)
            scr.write_text(lt, -2 - len(lt), y + 1)

        conn.write(scr.to_bytes())


if __name__ == '__main__':
    port = int(sys.argv[1]) if len(sys.argv) > 1 else 5003

    server = SnakeServer(port)
    server.start()

