import psycopg2

# TODO: Build functions to add data


def connect_to_db():
    conn = psycopg2.connect("host='localhost' dbname='shelf' user='bloo' password='Loading...'")
    return conn


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
        query = "INSERT INTO Trader(username, salt, psw) VALUES (%s, %s, %s)"
        info = [data['username'], data['salt'], data['password']]
        cur.execute(query, info)
        conn.commit()
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
        cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['sender']])
        sender_id = cur.fetchone()
        cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['receiver']])
        receiver_id = cur.fetchone()
        query = "INSERT INTO Request(sender_id, receiver_id, sender_key) VALUES (%s, %s, %s)"
        info = [sender_id, receiver_id, data['sender_key']]
        cur.execute(query, info)
        conn.commit()
        return "Success"
    except psycopg2.ProgrammingError as e:
        return e


# conn = psycopg2.connect("host='localhost' dbname='shelf' user='bloo' password='Loading...'")
# conn = connect_to_db()
# cur = conn.cursor()
# sender_id = cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", ["otus"])
# for tup in cur.fetchone():
#     print(tup)
