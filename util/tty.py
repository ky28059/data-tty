import os


def tty_to_fd(tty_id: int) -> int:
    tty_name = f"/dev/pts/{tty_id}"
    return os.open(tty_name, os.O_RDWR)


def tty_write(fd: int, data: bytes):
    os.write(fd, data)
