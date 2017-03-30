import json

from db import data_io

ACTION_DICT = {"verify": 1, "register": 2, "login": 3}


def parse_json(data):
    return json.loads(data)


def format_username(username):
    return '{"type": ' + str(ACTION_DICT["verify"]) + ', "username": "' + username + '"}'


def format_register_user(user):
    return '{"type": ' + str(ACTION_DICT["register"]) + ', "username": "' + user.name + \
           '","salt": "' + user.salt + '", "password": "' + user.psw + '"}'


def format_login(user):
    return '{"type": ' + str(ACTION_DICT["login"]) + ', "username": "' + user.name + \
           '", "password": "' + user.psw + '"}'


def handle(data):
    if data['type'] == 1:
        verification = data_io.verify_username(data['username'])
        if verification is None:
            return "None"
        else:
            return verification
    elif data['type'] == 2:
        return data_io.register_user(data)
    elif data['type'] == 3:
        return data_io.login_user(data)


