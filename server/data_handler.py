import json

from db import data_io

ACTION_DICT = {"verify": 1, "register": 2, "login": 3, "start conv": 4, "fetch received": 5,
               "fetch sent": 6, "req ans": 7, "fetch conv": 8, "enter conv": 9, "send": 10, "recv": 11}


def parse_json(data):
    """Parse data received from client into json data"""
    return json.loads(data)


def handle(data):

    """
    Handle the data according to its type
    See ACTION_DICT above for data types
    """

    if data['type'] == ACTION_DICT["verify"]:
        verification = data_io.verify_username(data['username'])
        if verification is None:
            return "None"
        else:
            return verification
    elif data['type'] == ACTION_DICT["register"]:
        return data_io.register_user(data)
    elif data['type'] == ACTION_DICT["login"]:
        return data_io.login_user(data)
    elif data['type'] == ACTION_DICT["start conv"]:
        return data_io.conv_req(data)
    elif data['type'] == ACTION_DICT["fetch received"]:
        reqs = data_io.fetch_received_request(data)
        if reqs is None:
            return "None"
        else:
            return reqs
    elif data['type'] == ACTION_DICT["req ans"]:
        return str(data_io.req_response(data))
    elif data['type'] == ACTION_DICT["fetch conv"]:
        return data_io.fetch_conv(data)
    elif data['type'] == ACTION_DICT["enter conv"]:
        auth = data_io.authenticate_conv(data)
        if auth:
            return data_io.enter_conv(data)
        return str(auth)
    elif data['type'] == ACTION_DICT["send"]:
        return data_io.save_messages(data)

