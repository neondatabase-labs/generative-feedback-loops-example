from psycopg2 import pool
from utils.config import DATABASE_URL

connection_pool = pool.SimpleConnectionPool(1, 10, DATABASE_URL)


def execute_query(query, params=None):
    conn = connection_pool.getconn()
    try:
        with conn.cursor() as cur:
            cur.execute(query, params)
            if query.strip().lower().startswith("select"):
                return cur.fetchall()
            conn.commit()
    finally:
        connection_pool.putconn(conn)
