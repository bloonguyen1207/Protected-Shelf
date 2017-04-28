import psycopg2


def connect_to_db():

    """
    Open connection to the database
    Change db here
    """

    conn = psycopg2.connect("host='localhost' dbname='shelf' user='bloo' password='Loading...'")
    return conn


def fetch_id_from_name(username):

    """Get user id from username"""

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s;", [username])
    return cur.fetchone()


def fetch_name_from_id(t_id):

    """Get username from user id"""

    conn = connect_to_db()
    cur = conn.cursor()
    cur.execute("SELECT username FROM Trader WHERE t_id=%s;", [t_id])
    return cur.fetchone()


def verify_username(username):

    """
    Check if username existed in the server db
    Use when register or login
    """

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        cur.execute("SELECT salt FROM Trader WHERE username LIKE %s;", [username])
        for tup in cur.fetchall():
            if tup[0] is not None:
                return tup[0]
            else:
                return "None"
    except psycopg2.ProgrammingError:
        return "Internal server error."


def register_user(data):

    """Create new user"""

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        query = "INSERT INTO Trader(username, salt, psw) VALUES (%s, %s, %s)"
        info = [data['username'], data['salt'], data['password']]
        cur.execute(query, info)
        conn.commit()
        conn.close()
        return "Success"
    except psycopg2.ProgrammingError:
        return "Internal server error."


def login_user(data):

    """Match username and password with existed data in the database"""

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        query = "SELECT psw FROM Trader WHERE username LIKE %s"
        info = [data['username']]
        cur.execute(query, info)
        for tup in cur.fetchall():
            return str(tup[0] == data['password'])
    except psycopg2.ProgrammingError:
        return "Internal server error."


def conv_req(data):

    """
    Create a new request when a user wants to start a new conversation
    Default status of request is 0, which means UNANSWERED
    """

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        # cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['sender']])
        sender_id = fetch_id_from_name(data['username'])
        # cur.execute("SELECT t_id FROM Trader WHERE username LIKE %s", [data['receiver']])
        receiver_id = fetch_id_from_name(data['receiver'])
        query = "INSERT INTO Request(sender_id, receiver_id, sender_key) VALUES (%s, %s, E%s)"
        info = [sender_id, receiver_id, data['sender_key']]
        cur.execute(query, info)
        conn.commit()
        conn.close()
        return "Success"
    except psycopg2.ProgrammingError:
        return "Internal server error."


def fetch_sent_request(data):

    """
    Fetch requests sent by user
    Map request status with string for better display
    Parse the parts into a string to send back to the user
    """

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        sender_id = fetch_id_from_name(data['username'])
        query = "SELECT r_id, receiver_id, status FROM Request WHERE sender_id=%s AND sender_key LIKE E%s"
        info = [sender_id, data['sender_key']]
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
    except psycopg2.ProgrammingError:
        return "Internal server error."


def fetch_received_request(data):

    """
    Fetch requests received by other users
    Map request status with string for better display
    Parse the parts into a string to send back to the user
    """

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
    except psycopg2.ProgrammingError:
        return "Internal server error."


def authenticate_req(data):

    """
    Check if the users is the correct receiver of the request
    Check if request is already answered
    Will be used when user try to respond to a request
    """

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        query = "SELECT receiver_id, status FROM Request WHERE r_id=%s"
        info = [data['req_id']]
        cur.execute(query, info)
        db_data = cur.fetchone()
        if db_data is None:
            return False
        receiver_id = db_data[0]
        status = db_data[1]
        if receiver_id is None or status != 0:
            return False
        name = fetch_name_from_id(receiver_id)[0]
        return name == data['username']
    except psycopg2.ProgrammingError:
        return "Internal server error."


def req_response(data):

    """
    Update request status from received data
    Create a new conversation if the request is accepted
    """

    conn = connect_to_db()
    cur = conn.cursor()

    auth = authenticate_req(data)
    if auth:

        # If accept then new conversation will be created in the db
        if data['answer'] == "yes" or data['answer'] == "y":
            status = 1
            cur.execute("SELECT sender_id, sender_key FROM Request WHERE r_id=%s", [data['req_id']])

            tup = cur.fetchone()

            t_id1 = tup[0]
            t1_key = tup[1]
            t_id2 = fetch_id_from_name(data['username'])
            t2_key = data['receiver_key']

            new_conv = "INSERT INTO Conversation(t_id1, t_id2, t1_key, t2_key) VALUES (%s, %s, E%s, E%s)"
            info = [t_id1, t_id2, t1_key, t2_key]
            cur.execute(new_conv, info)
            conn.commit()
        else:
            status = 2
        try:
            query = "UPDATE Request SET status=%s WHERE r_id=%s"
            info = [status, data['req_id']]
            cur.execute(query, info)
            conn.commit()
        except psycopg2.ProgrammingError:
            return "Internal server error."
    else:
        return False
    return True


def fetch_conv(data):

    """Fetch conversations where the user is a participant"""

    conn = connect_to_db()
    cur = conn.cursor()
    try:
        uid = fetch_id_from_name(data['username'])
        query = "SELECT * FROM Conversation WHERE (t_id1=%s OR t_id2=%s)" \
                "AND t1_key LIKE E%s OR t2_key LIKE E%s"
        info = [uid, uid, data['user_key'], data['user_key']]
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
    except psycopg2.ProgrammingError:
        return "Internal server error"


def authenticate_conv(data):

    """Check if user is a part of the conversation"""

    conn = connect_to_db()
    cur = conn.cursor()
    query = "SELECT * FROM Conversation WHERE c_id=%s AND (t1_key LIKE E%s OR t2_key LIKE E%s)"
    info = [data['cid'], data['user_key'], data['user_key']]
    cur.execute(query, info)
    tup = cur.fetchone()
    if tup is None:
        return False
    else:
        tid1 = tup[1]
        tid2 = tup[2]
        name1 = fetch_name_from_id(tid1)[0]
        name2 = fetch_name_from_id(tid2)[0]
        return name1 == data['username'] or name2 == data['username']


def enter_conv(data):

    """
    Retrieve data from a conversation when a user want to start chatting
    The request for this conversation must be accepted in order to enter it
    """

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

    return {"room": cid, name1+"_key": key1, name2+"_key": key2}


def save_messages(data):

    """
    Save message of sender and receiver to the db 
    to be fetched later if user wants to
    """

    conn = connect_to_db()
    cur = conn.cursor()
    rid = None
    uid = fetch_id_from_name(data['username'])
    try:
        query = "SELECT t_id1, t_id2 FROM Conversation WHERE c_id=%s"
        info = [data['room']]
        cur.execute(query, info)
        r = cur.fetchone()
        for i in r:
            if i != uid:
                rid = i
        new_sent_msg = "INSERT INTO message_sent(c_id, t_id, msg_content) VALUES (%s, %s, E%s)"
        info = [data['room'], uid, data['content']]
        cur.execute(new_sent_msg, info)
        conn.commit()

        new_recv_msg = "INSERT INTO message_received(c_id, t_id, msg_content) VALUES (%s, %s, E%s)"
        info = [data['room'], rid, data['content']]
        cur.execute(new_recv_msg, info)
        conn.commit()
        conn.close()
        return "Success"
    except psycopg2.ProgrammingError:
        return "Internal server error."

