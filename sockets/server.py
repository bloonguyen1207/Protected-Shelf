import select
import socket


CONNECTION_LIST = []


class ThreadedServer(object):

    # TODO: Multithread to handle clients
    def __init__(self, host, port):
        self.host = host
        self.port = port
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self.sock.bind((self.host, self.port))
        CONNECTION_LIST.append(self.sock)
        print(CONNECTION_LIST)

    def listen(self):
        self.sock.listen(5)
        read_sockets, write_sockets, error_sockets = select.select(CONNECTION_LIST, [], [])
        while True:
            print("dafuq am I doin here...")
            for s in read_sockets:
                print("???")
                if s == CONNECTION_LIST[0]:
                    client, address = self.sock.accept()
                    print("Got a connection from %s" % str(address))
                    CONNECTION_LIST.append(client)
                    print(CONNECTION_LIST)
                    broadcast_data(client, "[%s:%s] entered room\n" % address)
                    print("here now")
                else:
                    print("dafuq")
                    size = 2048
                    while True:
                        try:
                            data = s.recv(size)
                            print(str(address) + ": " + data.decode())
                            if data:
                                # Set the response to echo back the received data
                                broadcast_data(s, str(address) + ": " + data.decode())
                                print("Broadcasted.")
                        except:
                            broadcast_data(s, "Client (%s, %s) is offline" % address)
                            print("Client (%s, %s) is offline" % address)
                            s.close()
                            CONNECTION_LIST.remove(s)
                            print(CONNECTION_LIST)

    @staticmethod
    def listen_to_client(client, address):
        size = 2048
        while True:
            try:
                data = client.recv(size)
                print(str(address) + ": " + data.decode())
                if data:
                    # Set the response to echo back the received data
                    broadcast_data(client, address)
            except:
                broadcast_data(client, "Client (%s, %s) is offline" % address)
                print("Client (%s, %s) is offline" % client % address)
                client.close()
                CONNECTION_LIST.remove(client)
                continue


# Function to broadcast chat messages to all connected clients
def broadcast_data(client, message):
    # Do not send the message to master socket and the client who has send us the message
    for s in CONNECTION_LIST:
        if s != CONNECTION_LIST[0] and s != client:
            print("Waitin...")
            try:
                s.send(message.encode())
                if message != '':
                    print(message)
                else:
                    print('oi')
            except:
                # broken socket connection may be, chat client pressed ctrl+c for example
                s.close()
                CONNECTION_LIST.remove(socket)
                print(CONNECTION_LIST)


if __name__ == "__main__":
    p = 2222
    print("Server started on port: " + str(p))
    ThreadedServer('', 2222).listen()
