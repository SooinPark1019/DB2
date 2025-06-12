from db import db_cursor
from messages import *
from service.dvd_service import initialize_database

def reset():
    confirm = input("Are you sure you want to reset the database? (y/n): ").strip().lower()
    if confirm != 'y':
        print("Database reset canceled.")
        return
    with db_cursor() as (conn, cursor):
        cursor.execute("DROP TABLE IF EXISTS borrowing")
        cursor.execute("DROP TABLE IF EXISTS rate")
        cursor.execute("DROP TABLE IF EXISTS user")
        cursor.execute("DROP TABLE IF EXISTS dvd")
    # 곧바로 재초기화
    initialize_database()
