import json
import socket

from db import data_io

ACTION_DICT = {"verify": 1, "register": 2, "login": 3}


def parse_json(data):
    return json.loads(data)


def format_username(username):
    return '{"type": ' + str(ACTION_DICT["verify"]) + ', "username": "' + username + '"}'


def register_user(user):
    return '{"type": ' + str(ACTION_DICT["register"]) + ', "username": "' + user.name + \
           '","salt": "' + user.salt + '", password": "' + user.psw + '"}'


def handle(conn, data):
    if data['type'] == 1:
        verification = data_io.verify_username(data['username'])
        print(verification)
        try:
            conn.send(str(verification).encode())
        except socket.error as e:
            print(e)
    # elif data['type'] == 2:
