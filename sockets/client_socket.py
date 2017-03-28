# telnet program example
import socket
import select
import sys


# TODO: add send message function
class ClientSocket:
    def __init__(self, sock=None):
        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def open_connection(self, host, port):
        try:
            self.sock.connect((host, port))
            print("Connected to remote host. Start sending messages\n Type 'exit.' to disconnect.")
            # self.prompt()
        except socket.error as e:
            print("Cannot connect to host.")
            print(e)
            print("Please try again later.")
            sys.exit()

    def close_connection(self):
        try:
            self.sock.close()
        except socket.error as e:
            print("Error closing connection: %s", e)

    def send_message(self, message):
        total_sent = 0
        while total_sent < 4096:
            sent = self.sock.send(message[total_sent:].encode())
            if sent != 0:
                break
            return self.sock.recv(4096).decode()
                # print(message)
                # socket_list = [input, self.sock]
                # read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

                # for sock in read_sockets:
                # if self.sock:
                #     data = self.sock.recv(4096)
                #     if not data:
                #         print(data)
                #         print('\nDisconnected from server.')
                #         sys.exit()
                #     else:
                #         # Print data
                #         sys.stdout.write(data.decode())
                # else:
                #     try:
                #         self.sock.send(message.encode())
                #     except socket.error as e:
                #         print("Caught error: %s", e)

    def in_conversation(self):
        socket_list = [sys.stdin, self.sock]

        # Get the list sockets which are readable
        read_sockets, write_sockets, error_sockets = select.select(socket_list, [], [])

        for sock in read_sockets:
            # Incoming message from remote server
            if sock == self.sock:
                data = sock.recv(4096)
                if not data:
                    # print(data)
                    print('\nDisconnected from chat server.')
                    sys.exit()
                else:
                    # Print data
                    sys.stdout.write(data.decode())
                    self.prompt()
            # User entered a message
            else:
                msg = sys.stdin.readline()
                self.sock.send(msg.encode())
                self.prompt()

    @staticmethod
    def prompt():
        sys.stdout.write('>> ')
        sys.stdout.flush()


# main function
if __name__ == "__main__":
     
    if len(sys.argv) < 3:
        print('Usage : python client_socket.py hostname port')
        sys.exit()
     
    host = sys.argv[1]
    port = int(sys.argv[2])
     
    s = ClientSocket()
     
    # connect to remote host
    s.open_connection(host, port)
     
    while 1:
        s.in_conversation()
