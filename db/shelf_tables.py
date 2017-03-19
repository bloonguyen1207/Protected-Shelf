import psycopg2

conn = psycopg2.connect("dbname=shelf user=bloo")

cur = conn.cursor()
