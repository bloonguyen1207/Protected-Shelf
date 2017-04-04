import psycopg2


# TODO: Build functions to add data


def connect_to_db():
    conn = psycopg2.connect("host='localhost' dbname='shelf' user='bloo' password='Loading...'")
    return conn


def fetch_id_from_name(username):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s;", [username])
    return cur.fetchone()


def fetch_name_from_id(t_id):
    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT username FROM Trader WHERE t_id=%s;", [t_id])
    return cur.fetchone()


def verify_username(username):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT salt FROM Trader WHERE username LIKE %s;", [username])
        for tup in cur.fetchall():
            if tup[0] is not None:
                return tup[0]
            else:
                return "None"
    except psycopg2.ProgrammingError as e:
        return e


def register_user(data):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        query = "INSERT INTO Trader(username, salt, psw) VALUES (%S, %S, %S)"
        info = [data['username'], data['salt'], data['password']]
        cur.execute(query, info)
        conn.commit()
        conn.close()
        return "Success"
    except psycopg2.ProgrammingError as e:
        return e


def login_user(data):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        query = "SELECT psw FROM Trader WHERE username LIKE %s"
        info = [data['username']]
        cur.execute(query, info)
        for tup in cur.fetchall():
            return str(tup[0] == data['password'])
    except psycopg2.ProgrammingError as e:
        return e


def conv_req(data):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        # cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['sender']])
        sender_id = fetch_id_from_name(data['sender'])
        # cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['receiver']])
        receiver_id = fetch_id_from_name(data['receiver'])
        query = "INSERT INTO Request(sender_id, receiver_id, sender_key) VALUES (%S, %S, %S)"
        info = [sender_id, receiver_id, data['sender_key']]
        cur.execute(query, info)
        conn.commit()
        conn.close()
        return "Success"
    except psycopg2.ProgrammingError as e:
        return e


def fetch_received_request(data):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        recv_id = fetch_id_from_name(data['username'])
        query = "SELECT r_id, sender_id, status FROM Request WHERE receiver_id=%s"
        info = [recv_id]
        cur.execute(query, info)
        l = []
        for tup in cur.fetchall():
            sender_name = fetch_name_from_id(tup[1])[0]
            if tup[2] == 0:
                status = "UNANSWERED"
            elif tup[2] == 1:
                status = "ACCEPTED"
            else:
                status = "DECLINED"
            l.append(' '.join([str(tup[0]), sender_name, status]))
        if not l:
            return "None"
        else:
            return ', '.join(l)
    except psycopg2.ProgrammingError as e:
        return e


def authenticate_req(data):
    conn = connect_to_db()
    cur = conn.cursor()
    query = "SELECT receiver_id FROM Request WHERE r_id=%s"
    info = [data['req_id']]
    cur.execute(query, info)
    receiver_id = cur.fetchone()
    name = fetch_name_from_id(receiver_id)[0]
    return name == data['username']


def req_response(data):
    conn = connect_to_db()
    cur = conn.cursor()
    if data['answer'] == "yes" or data['answer'] == "y":
        status = 1
        # TODO: start new conversation in here
    else:
        status = 2
    query = "UPDATE Request SET status=%s WHERE r_id=%s"
    info = [status, data['req_id']]
    cur.execute(query, info)

# conn = psycopg2.connect("host='localhost' dbname='shelf' user='bloo' password='Loading...'")
# conn = connect_to_db()
# cur = conn.cursor()
# recv_id = fetch_id_from_name("barney")
# query = "SELECT r_id, sender_id, status FROM Request WHERE receiver_id=%s"
# info = [recv_id]
# cur.execute(query, info)
# l = []
# for tup in cur.fetchall():
#     l.append(' '.join(map(str, tup)))
#
# if not l:
#     print("nah")
# else:
#     print(', '.join(l))
