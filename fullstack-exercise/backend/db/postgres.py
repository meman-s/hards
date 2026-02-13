import psycopg2

conn = None


def init_postgres(url):
    global conn
    conn = psycopg2.connect(url)


def close_postgres():
    global conn
    if conn:
        conn.close()
        conn = None
