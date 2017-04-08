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
        sender_id = fetch_id_from_name(data['username'])
        # cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['receiver']])
        receiver_id = fetch_id_from_name(data['receiver'])
        query = "INSERT INTO Request(sender_id, receiver_id, sender_key) VALUES (%s, %s, %s)"
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
    if receiver_id is None:
        return False
    name = fetch_name_from_id(receiver_id)[0]
    return name == data['username']


def req_response(data):
    conn = connect_to_db()
    cur = conn.cursor()

    auth = authenticate_req(data)
    if auth:
        if data['answer'] == "yes" or data['answer'] == "y":
            status = 1
            # TODO: start new conversation in here v
            # New
            cur.execute("SELECT sender_id, sender_key FROM Request WHERE r_id=%s", [data['req_id']])
            tup = cur.fetchone()
            t_id1 = tup[0]
            t1_key = tup[1]
            t_id2 = fetch_id_from_name(data['username'])
            t2_key = data['receiver_key']
            new_conv = "INSERT INTO Conversation(t_id1, t_id2, t1_key, t2_key) VALUES (%s, %s, %s, %s)"
            info = [t_id1, t_id2, t1_key, t2_key]
            cur.execute(new_conv, info)
            conn.commit()
            # -----------
        else:
            status = 2
        query = "UPDATE Request SET status=%s WHERE r_id=%s"
        info = [status, data['req_id']]
        cur.execute(query, info)
        conn.commit()
    else:
        return False
    return True


def fetch_conv(data):
    conn = connect_to_db()
    cur = conn.cursor()
    try:
        uid = fetch_id_from_name(data['username'])
        query = "SELECT * FROM Conversation WHERE (t_id1=%s OR t_id2=%s)"
        info = [uid, uid]
        cur.execute(query, info)
        l = []
        for tup in cur.fetchall():
            uname1 = fetch_name_from_id(tup[1])[0]
            uname2 = fetch_name_from_id(tup[2])[0]
            l.append(' '.join([str(tup[0]), uname1, uname2]))
        if not l:
            return "None"
        else:
            return ', '.join(l)
    except psycopg2.ProgrammingError as e:
        return str(e)


def authenticate_conv(data):
    conn = connect_to_db()
    cur = conn.cursor()
    query = "SELECT t_id1, t_id2 FROM Conversation WHERE c_id=%s"
    info = [data['cid']]
    cur.execute(query, info)
    tup = cur.fetchone()
    if tup is None:
        return False
    else:
        tid1 = tup[0]
        tid2 = tup[1]
        name1 = fetch_name_from_id(tid1)[0]
        name2 = fetch_name_from_id(tid2)[0]
        return name1 == data['username'] or name2 == data['username']


def enter_conv(data):
    conn = connect_to_db()
    cur = conn.cursor()
    query = "SELECT * FROM Conversation WHERE c_id=%s"
    info = [data['cid']]
    try:
        cur.execute(query, info)
        tup = cur.fetchone()
    except psycopg2.ProgrammingError:
        return "Internal server error."
    cid = tup[0]
    tid1 = tup[1]
    tid2 = tup[2]
    key1 = tup[3]
    key2 = tup[4]
    name1 = fetch_name_from_id(tid1)[0]
    name2 = fetch_name_from_id(tid2)[0]

    return {'room': cid, name1+'_key': key1, name2+'_key': key2}
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
