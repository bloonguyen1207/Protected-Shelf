import json

# re-format inputs from user into a json-like string to handle in the server

ACTION_DICT = {"verify": 1, "register": 2, "login": 3, "start conv": 4, "fetch received": 5,
               "fetch sent": 6, "req ans": 7, "fetch conv": 8, "enter conv": 9, "send": 10, "recv": 11}


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
           ', "username": "' + sender_name + '", "receiver": "' + \
           receiver_name + '", "sender_key": "' + key.replace('\n', '\\\\n') + '"}'


def format_received_request(user):
    return '{"type": ' + str(ACTION_DICT["fetch received"]) + \
           ', "username": "' + user.name + '"}'


def format_sent_request(user):
    return '{"type": ' + str(ACTION_DICT["fetch sent"]) + \
           ', "username": "' + user.name + '", "sender_key": "' + \
           user.publickey().replace('\n', '\\\\n') + '"}'


def format_answer(user, req_id, ans):
    return '{"type": ' + str(ACTION_DICT["req ans"]) + \
           ', "req_id": ' + req_id + ',"answer": "' + ans + \
           '", "username": "' + user.name + '", "receiver_key": "' + \
           user.publickey().replace('\n', '\\\\n') + '"}'


def format_fetch_conv(user):
    return '{"type": ' + str(ACTION_DICT["fetch conv"]) + \
           ', "username": "' + user.name + '", "user_key": "' + \
           user.publickey().replace('\n', '\\\\n') + '"}'


def format_enter_conv(user, cid):
    return '{"type": ' + str(ACTION_DICT["enter conv"]) + \
           ', "username": "' + user.name + '", "user_key": "' + \
           user.publickey().replace('\n', '\\\\n') + '", "cid":' + str(cid) + '}'


def format_sent_message(username, message, room):
    return '{"type": ' + str(ACTION_DICT["send"]) + \
           ', "username": "' + username + '", "content":"' + \
           message.strip() + '", "room": ' + str(room) + '}'


