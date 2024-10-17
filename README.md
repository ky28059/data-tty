# data-tty
 `write`-based game clients for `data.cs.purdue.edu`.

![image](https://github.com/user-attachments/assets/2820e71a-ae2e-40df-87ae-8881ae4d4504)

### Usage
SSH into `data.cs.purdue.edu` as usual, e.g.
```bash
ssh [username]@data.cs.purdue.edu
```
Then, run
```bash
python3 /homes/tan478/data-tty/client.py [port]
```
to join the game being run on the specified port.

![image](https://github.com/user-attachments/assets/094c909e-6d66-4340-be9b-c42c538f93ef)

To *host* a game on `data`, clone the repository and mark `client.py` as readable + executable:
```bash
git clone https://github.com/ky28059/data-tty
chmod 755 ./data-tty/client.py
```
Then, you can run a game server on a specific port by running the desired file in `/games`, passing a port as the first
command-line argument (e.g. to run a chat server on port 5003,
```bash
python3 ./data-tty/games/chat.py 5003
```

### Motivation
The idea behind this project was to run a multiplayer game on `data.cs.purdue.edu` using only the `write` command.

Unfortunately, because scripts cannot programmatically *read* text that was written to a user, client → server
communication still needs to occur over a TCP socket.

Still, these games are "server-side rendered" because `client.py` has no logic to display any game state to the
user's terminal; instead, the client sends keypresses and terminal information (e.g. screen size) to the server and the
server renders the game display directly to the client via `write`.
