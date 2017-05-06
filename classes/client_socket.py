# telnet program example
import socket
import select
import sys

import binascii

from app import data_handler


class ClientSocket:
    def __init__(self, sock=None):

        """Create the client socket"""

        if sock is None:
            self.sock = socket.socket(
                socket.AF_INET, socket.SOCK_STREAM)
        else:
            self.sock = sock

    def open_connection(self, host, port):

        """Open a connection to the server"""

        try:
            self.sock.connect((host, port))
            # self.prompt()
        except socket.error as e:
            print("Cannot connect to host.")
            print(e)
            print("Please try again later.")
            sys.exit()

    def close_connection(self):

        """Close socket connection"""

        try:
            self.sock.close()
        except socket.error as e:
            print("Error closing connection: %s", e)

    def send_message(self, message):

        """
        Send message to the server
        This only runs once
        Open -> send -> close
        """

        total_sent = 0
        while total_sent < 2048:
            self.sock.send(message[total_sent:].encode())
            return self.sock.recv(2048).decode()

    def in_conversation(self, user, room, key):

        """
        Get user in a loop to chat with each other
        Keep exchange data
        Open -> send & receive
        Stop when user types 'exit.' or press 'Ctrl + C'
        """

        while 1:
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
                        # Load user private key to decrypt message from other user
                        my_key = user.load_key(user.my_key())

                        # Split actual data with username - done
                        raw_data = data.decode().split(' ')
                        f_name = raw_data[0]
                        raw_message = raw_data[-1]

                        # Encrypted message always have the length of 512
                        # None of the server announcement have same length
                        if len(raw_message) == 512:
                            cipher_message = binascii.unhexlify(raw_message.encode())
                            decrypted = my_key.decrypt(cipher_message)
                            sys.stdout.write(f_name + ' ' + decrypted.decode())
                        else:
                            not_message = data.decode()
                            sys.stdout.write(not_message + '\n')

                        self.prompt()

                # User entered a message
                else:
                    raw_msg = sys.stdin.readline()

                    if raw_msg != "\n":

                        # Encrypt the message with other user public key
                        # convert it to a string
                        msg = key.encrypt(raw_msg.encode(), 32)[0]
                        processed_msg = binascii.hexlify(msg).decode()
                        req = data_handler.format_sent_message(user.name, processed_msg, room)
                        self.send_message(req)

                    self.prompt()

    @staticmethod
    def prompt():
        sys.stdout.write('>> ')
        sys.stdout.flush()

