import socket
import threading
import time

server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
server.bind(("localhost", 6969))


def handle_conn(conn: socket.socket, address):
    while True:
        user_input = conn.recv(1)
        if not user_input:
            break
        print(address, user_input)


def accept_conn():
    print("Started server")
    server.listen()
    while True:
        (clientsocket, address) = server.accept()
        print("new connection", clientsocket, address)
        threading.Thread(target=handle_conn, args=(clientsocket, address)).start()


accept_thread = threading.Thread(target=accept_conn, daemon=True)
accept_thread.start()

while True:
    try:
        time.sleep(0.5)
    except KeyboardInterrupt:
        print("killed")
        break

accept_thread.join(1)
server.close()
