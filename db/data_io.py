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
            return tup[0]
    except psycopg2.ProgrammingError as e:
        return e


print(verify_username("bbbb"))
