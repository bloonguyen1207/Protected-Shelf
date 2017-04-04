import json

from db import data_io

ACTION_DICT = {"verify": 1, "register": 2, "login": 3, "start conv": 4, "fetch received": 5,
               "fetch sent": 6, "req ans": 7}


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


def format_req(sender_name, receiver_name, key):
    return '{"type": ' + str(ACTION_DICT["start conv"]) + \
           ', "sender": "' + sender_name + '", "receiver": "' + \
           receiver_name + '", "sender_key": "' + key.replace('\n', '\\\\n') + '"}'


def format_received_request(user):
    return '{"type": ' + str(ACTION_DICT["fetch received"]) + \
           ', "username": "' + user.name + '"}'


def format_sent_request(user):
    return '{"type": ' + str(ACTION_DICT["fetch sent"]) + \
           ', "username": "' + user.name + '", "sender_key": "' + user.publickey().replace('\n', '\\\\n') + '"}'


def format_answer(user, req_id, ans):
    return '{"type": ' + str(ACTION_DICT["req ans"]) + \
           ', "req_id": ' + req_id + ',"answer": " ' + ans + '", "username": "' + user.name + \
           '", "receiver_key": "' + user.publickey().replace('\n', '\\\\n') + '"}'


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
    elif data['type'] == 4:
        return data_io.conv_req(data)
    elif data['type'] == 5:
        reqs = data_io.fetch_received_request(data)
        if reqs is None:
            return "None"
        else:
            return reqs
    elif data['type'] == 7:
        auth = data_io.authenticate_req(data)


