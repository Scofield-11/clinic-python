import pymysql
def get_connection():
    conn = pymysql.connect(
        host="localhost",
        user="root",
        password="",
        database="clinic_db",
        cursorclass=pymysql.cursors.DictCursor
    )
    return conn