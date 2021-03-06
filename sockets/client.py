import socket

# Use client_socket.py
# Not this one


class ClientSocket:

    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def open_connection(self, host, port):
        self.sock.connect((host, port))

    def send_msg(self, msg):
        total_sent = 0
        while total_sent < 2048:
            sent = self.sock.send(msg[total_sent:].encode())
            print(self.sock.recv(2048).decode())
            if sent != 0:
                break

    def close_connection(self):
        self.sock.close()


if __name__ == "__main__":
    h = "localhost"
    p = 2222
    s = ClientSocket()
    s.open_connection(h, p)
    while True:
        inp = input("Type your message: ")
        s.send_msg(inp)
