# telnet program example
import codecs
import socket
import select
import sys

import binascii

from app import data_handler
from classes.user import User


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
            # print("Connected to remote host. Start sending messages\n Type 'exit.' to disconnect.")
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
        while total_sent < 2048:
            self.sock.send(message[total_sent:].encode())
            return self.sock.recv(2048).decode()
            # if sent != 0:
            #     break
            # return recv

    def in_conversation(self, user, room, key):
        while 1:
            get_out = False
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
                        my_key = user.load_key(user.my_key())
                        # TODO: Split actual data with username - done
                        raw_data = data.decode().split(' ')
                        f_name = raw_data[0]
                        raw_message = raw_data[1]

                        if len(raw_message) == 512:
                            cipher_message = binascii.unhexlify(raw_message.encode())
                            decrypted = my_key.decrypt(cipher_message)
                            # print(decrypted)
                            sys.stdout.write(f_name + ' ' + decrypted.decode())
                        else:
                            not_message = data.decode()
                            sys.stdout.write(not_message + '\n')

                        self.prompt()

                # User entered a message
                else:
                    raw_msg = sys.stdin.readline()

                    if raw_msg != "exit.\n":
                        msg = key.encrypt(raw_msg.encode(), 32)[0]
                        processed_msg = binascii.hexlify(msg).decode()
                        req = data_handler.format_sent_message(user.name, processed_msg, room)
                        self.send_message(req)
                        self.prompt()
                    else:
                        get_out = True
                        break

            if get_out:
                break

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
     
    # while 1:
        # s.in_conversation()
