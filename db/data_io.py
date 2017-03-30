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
