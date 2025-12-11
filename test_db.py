from app import get_connection
def lay_bs():
    conn = get_connection()
    try:
        with conn.cursor() as cur:
            cur.execute("SELECT*FROM BAC_SI")
            ls = cur.fetchall()
            for i in ls:
                print(i)
    finally:
        conn.close()
lay_bs()