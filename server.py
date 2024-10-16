import os
import socket
import struct
import sys
import threading
import time
import traceback

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", int(sys.argv[1])))

class BasePlayer:
    def __init__(self, socket: socket.socket):
        self.socket = socket
        self.game: BaseGame = None

        # get pty_id
        socket.settimeout(1)
        packet_type = socket.recv(1)
        if packet_type != b'\x01':
            raise Exception(f"Missing tty packet {packet_type}")
        socket.settimeout(None)
        self.tty_id = self.get_int()
        self.tty_name = f"/dev/pts/{self.tty_id}" # how do we stop people from impersonating? client can say they are a different tty
        # also do we want to hide /dev/pty since it's risky

        print(self.tty_id, self.tty_name)

        self.fd = os.open(self.tty_name, os.O_RDWR) # can error
        print(self.fd)
        self._open = True
        self.ev_thread = threading.Thread(target=self.packet_handler, args=(), daemon=True)
        self.ev_thread.start()

    def get_int(self):
        self.socket.settimeout(1)
        value = struct.unpack("<i", self.socket.recv(4))
        self.socket.settimeout(None)
        return value[0]

    def packet_handler(self):
        while True:
            try:
                packet_type = self.socket.recv(1)
                if not packet_type:
                    break
                match packet_type:
                    case b'\x01': # id packet
                        raise Exception("Disallowed tty packet")
                    case b'\x02': # resize packet
                        width = self.get_int()
                        height = self.get_int()
                        print(f"New window: {width}, {height}")
                    case b'\x04': # char input
                        c = self.socket.recv(1)
                        self.on_input(c)
                    case _:
                        raise Exception(f"Invalid packet type {ord(packet_type)}")
            except Exception as e:
                print(e)
                print(traceback.format_exc())

                self.close()
                return
        self.close()
        self.on_disconnect()


    def write(self, data: bytes):
        if not self.socket:
            raise Exception("Player is already closed")
        try:
            os.write(self.fd, data)
        except:
            print("failed to write", self.fd)

    def close(self):
        if not self._open:
            raise Exception("Player is already closed")
        print("Closing")
        os.close(self.fd)
        self.socket.close()
        self._open = False
        if self.game:
            self.game.remove_player(self)

    def on_disconnect(self):
        pass

    def on_input(self, key: bytes):
        pass


class BaseGame:
    def __init__(self):
        self.players: list[BasePlayer] = []

    def add_player(self, player: BasePlayer):
        player.game = self
        self.players.append(player)
        self.on_join(player)

    def remove_player(self, player: BasePlayer):
        self.players.remove(player)
        self.on_leave(player)

    def on_join(self, player: BasePlayer):
        pass

    def on_leave(self, player: BasePlayer):
        pass

    def update():
        pass

class SnakePlayer(BasePlayer):
    def __init__(self, socket: socket.socket):
        super().__init__(socket)
        self.x = 0
        self.y = 0

    def on_input(self, key: bytes):
        match(key):
            case b"a":
                self.x -= 1
            case b"d":
                self.x += 1
            case b"w":
                self.y -= 1
            case b"s":
                self.y += 1

class SnakeGame(BaseGame):
    players: list[SnakePlayer]
    def on_join(self, player: BasePlayer):
        print(f"new player {player.tty_id}")

    def update(self):
        for player in self.players:
            player.write(f"\x1b[2Kx: {player.x} y: {player.y}\r".encode())
        time.sleep(0.1)


GAME = SnakeGame()



def handle_conn(conn: socket.socket):
    try:
        player = SnakePlayer(conn)
    except Exception as e:
        print(f"Failed to create player: {e}")

        print(traceback.format_exc())
        conn.close()
        return
    GAME.add_player(player)

def accept_conn():
    print("Started server")
    server.listen()
    while True:
        (clientsocket, address) = server.accept()
        print("new connection", clientsocket, address)
        threading.Thread(target=handle_conn, args=(clientsocket,)).start()


accept_thread = threading.Thread(target=accept_conn, daemon=True)
accept_thread.start()

while True:
    try:
        GAME.update()
    except KeyboardInterrupt:
        print("killed")
        break

accept_thread.join(0.2)
server.close()
