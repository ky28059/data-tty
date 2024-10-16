from util.game_server import GameServer

if __name__ == '__main__':
    server = GameServer(
        port=5003,
        on_connect=print,
        on_input=print
    )

    server.start()
    server.join()
