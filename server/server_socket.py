# -------------------------------------------------------------------------------
# Basic echo server using the selectors module.
#
# Based on the example provided in the documentation.
#
# Eli Bendersky (eliben@gmail.com)
# This code is in hte public domain
# -------------------------------------------------------------------------------
# Bloo added a bit to enable messages broadcasting between clients
# Will work on this more
# Wait for it
# -------------------------------------------------------------------------------
import logging
import selectors
import socket
import time
from server import data_handler

HOST = 'localhost'
PORT = 2222

logging.basicConfig(level=logging.INFO, format='[%(asctime)s] %(message)s')

CONNECTION_LIST = []
ROOMS = []
ROOMS_INFO = []


# TODO: parse data from string -> json -> Done
class SelectorServer:
    def __init__(self, host, port):
        # Create the main socket that accepts incoming connections and start
        # listening. The socket is nonblocking.
        self.main_socket = socket.socket()
        self.main_socket.bind((host, port))
        self.main_socket.listen(100)
        self.main_socket.setblocking(False)

        # Create the selector object that will dispatch events. Register
        # interest in read events, that include incoming connections.
        # The handler method is passed in data so we can fetch it in
        # serve_forever.
        self.selector = selectors.DefaultSelector()
        self.selector.register(fileobj=self.main_socket,
                               events=selectors.EVENT_READ,
                               data=self.on_accept)

        CONNECTION_LIST.append(self.main_socket)
        # Keeps track of the peers currently connected. Maps socket fd to
        # peer name.
        self.current_peers = {}

    def on_accept(self, sock, mask):
        # This is a handler for the main_socket which is now listening, so we
        # know it's ready to accept a new connection.
        conn, addr = self.main_socket.accept()
        logging.info('accepted connection from {0}'.format(addr))
        conn.setblocking(False)

        self.current_peers[conn.fileno()] = conn.getpeername()
        # Register interest in read events on the new socket, dispatching to
        # self.on_read
        self.selector.register(fileobj=conn, events=selectors.EVENT_READ,
                               data=self.on_read)
        CONNECTION_LIST.append(conn)
        # broadcast_data(conn, ("[%s:%s] entered room\n" % addr).encode())

    def close_connection(self, conn):
        # We can't ask conn for getpeername() here, because the peer may no
        # longer exist (hung up); instead we use our own mapping of socket
        # fds to peer names - our socket fd is still open.
        peer_name = self.current_peers[conn.fileno()]
        logging.info('closing connection to {0}'.format(peer_name))
        # broadcast_data(conn, (str(peer_name) + " left.\n").encode())
        del self.current_peers[conn.fileno()]
        self.selector.unregister(conn)
        if conn in CONNECTION_LIST:
            CONNECTION_LIST.remove(conn)
        conn.close()

    def on_read(self, conn, mask):
        # This is a handler for peer sockets - it's called when there's new
        # data.
        try:
            data = conn.recv(4096)
            if data:
                peer_name = conn.getpeername()
                logging.info('got data from {}: {!r}'.format(peer_name, data.decode()))

                # TODO: Separate different types of requests -> see data_handler.py
                json_data = data_handler.parse_json(data.decode())
                try:
                    # TODO: Broadcast message first then room later
                    handled_data = str(data_handler.handle(json_data))
                    conn.send(handled_data.encode())
                    print(handled_data)
                    if json_data['type'] == 9:
                        if json_data['cid'] not in ROOMS:
                            r = {'room': json_data['cid'], json_data['username']: conn, 'server': self.main_socket}
                            ROOMS_INFO.append(r)
                            ROOMS.append(json_data['cid'])
                        else:
                            for data in ROOMS_INFO:
                                if data['room'] == json_data['cid']:
                                    data[json_data['username']] = conn
                                    for k, v in data.copy().items():
                                        if v != data['room'] and v not in CONNECTION_LIST:
                                            del data[k]
                                    if len(data) > 3:
                                        broadcast_data(conn, (json_data['username'] +
                                                              " entered the chat room.").encode(), data)
                        print(ROOMS)
                        print(ROOMS_INFO)
                    if json_data['type'] == 10:
                        room = {}
                        for data in ROOMS_INFO:
                            if json_data['room'] == data['room']:
                                room = data
                        if json_data['content'] != "exit.":
                            broadcast_data(conn, ("[" + json_data['username'] + "]: " + json_data['content']).encode(), room)
                        else:

                            del room[json_data['username']]
                            self.close_connection(conn)

                except socket.error as e:
                    print(e)
            else:
                if conn in CONNECTION_LIST:
                    CONNECTION_LIST.remove(conn)

                for data in ROOMS_INFO:
                    for k, v in data.copy().items():
                        if v != data['room'] and v not in CONNECTION_LIST:
                            del data[k]
                    if len(data) > 2:
                        broadcast_data(conn, "The other user left the chat room.".encode(), data)
                print(ROOMS_INFO)
                self.close_connection(conn)
        except ConnectionResetError:
            if conn in CONNECTION_LIST:
                CONNECTION_LIST.remove(conn)
            self.close_connection(conn)

    def serve_forever(self):
        last_report_time = time.time()

        while True:
            # Wait until some registered socket becomes ready. This will block
            # for 200 ms.
            events = self.selector.select(timeout=0.2)
            # print()
            # For each new event, dispatch to its handler
            for key, mask in events:
                handler = key.data
                handler(key.fileobj, mask)

            # This part happens roughly every second.
            cur_time = time.time()
            if cur_time - last_report_time > 1:
                logging.info('Running report...')
                logging.info('Num active peers = {0}'.format(
                    len(self.current_peers)))
                last_report_time = cur_time


def broadcast_data(client, message, room):
    # Do not send the message to master socket and the client who has send us the message
    # for s in CONNECTION_LIST:
    #     if s != CONNECTION_LIST[0] and s != client:
    #         try:
    #             s.send(message)
    #         except socket.error as e:
    #             # broken socket connection may be, chat client pressed ctrl+c for example
    #             if s in CONNECTION_LIST:
    #                 CONNECTION_LIST.remove(s)
    #             s.close()
    #             print("Error caught: %s", e)

    for k in room.keys():
        if k != 'room' and room[k] != client and k != "server":
            try:
                room[k].send(message)
            except socket.error as e:
                # broken socket connection may be, chat client pressed ctrl+c for example
                if room[k] in CONNECTION_LIST:
                    CONNECTION_LIST.remove(room[k])
                room[k].close()
                del room[k]
                print("Error caught: %s", e)

if __name__ == '__main__':
    logging.info('starting')
    server = SelectorServer(host=HOST, port=PORT)
    server.serve_forever()
