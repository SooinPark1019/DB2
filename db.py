import mysql.connector
from contextlib import contextmanager

DB_CONFIG = {
    'host': 'astronaut.snu.ac.kr',
    'port': 7001,
    'user': 'DB2020_14316',
    'password': 'DB2020_14316',
    'database': 'DB2020_14316',
    'charset': 'utf8'
}

def get_connection():
    """MySQL DB Connection 반환"""
    return mysql.connector.connect(
        host=DB_CONFIG['host'],
        port=DB_CONFIG['port'],
        user=DB_CONFIG['user'],
        password=DB_CONFIG['password'],
        database=DB_CONFIG['database'],
        charset=DB_CONFIG['charset'],
        autocommit=False
    )

@contextmanager
def db_cursor(dictionary=False):
    """
    with db_cursor() as (conn, cursor):
        # 쿼리 ...
    커밋/롤백/종료 자동 처리
    """
    conn = get_connection()
    try:
        with conn.cursor(dictionary=dictionary) as cursor:
            yield conn, cursor
        conn.commit()  # 정상 종료 시 커밋
    except Exception as e:
        conn.rollback()  # 에러 시 롤백
        raise
    finally:
        conn.close()