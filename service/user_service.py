from db import db_cursor
from util import format_rating, print_table, validate_length, to_positive_int
from messages import *

def print_users():
    headers = ['id', 'name', 'age', 'avg.rating', 'cumul_rent_cnt']
    rows = []

    with db_cursor(dictionary=True) as (conn, cursor):
        # 모든 유저 정보, 평균 평점, 누적 대출 횟수
        cursor.execute("""
            SELECT
                u.u_id,
                u.u_name,
                u.u_age,
                AVG(r.rating) AS avg_rating,
                COUNT(b.b_id) AS cumul_rent_cnt
            FROM user u
            LEFT JOIN rate r ON u.u_id = r.u_id
            LEFT JOIN borrowing b ON u.u_id = b.u_id
            GROUP BY u.u_id, u.u_name, u.u_age
            ORDER BY u.u_id
        """)
        for row in cursor.fetchall():
            avg_rating = row['avg_rating']
            avg_rating_str = format_rating(avg_rating) if avg_rating is not None else 'None'
            cumul_rent_cnt = row['cumul_rent_cnt']
            rows.append([
                row['u_id'],
                row['u_name'],
                row['u_age'],
                avg_rating_str,
                cumul_rent_cnt
            ])

    print('-' * 80)
    print_table(headers, rows)
    print('-' * 80)

def insert_user():
    name = input('User name: ').strip()
    age = input('User age: ').strip()

    # 1. 이름 길이 체크 (1~30자)
    if not validate_length(name, 1, 30):
        print(ERR_USERNAME_LENGTH)
        return

    # 2. 나이 체크 (양의 정수)
    age_int = to_positive_int(age)
    if age_int is None:
        print(ERR_USER_AGE)
        return

    # 3. INSERT
    with db_cursor() as (conn, cursor):
        cursor.execute(
            "INSERT INTO user (u_name, u_age, overdue_score, penalty_left) VALUES (%s, %s, 0, 0)",
            (name, age_int)
        )
    print(MSG_USER_INSERT)

def remove_user():
    user_id_input = input('User ID: ').strip()
    user_id = to_positive_int(user_id_input)
    if user_id is None:
        print(ERR_USER_NOT_EXIST.format(user_id_input))
        return

    with db_cursor() as (conn, cursor):
        # 1. 회원 존재 여부 체크
        cursor.execute("SELECT 1 FROM user WHERE u_id = %s", (user_id,))
        if not cursor.fetchone():
            print(ERR_USER_NOT_EXIST.format(user_id))
            return

        # 2. 회원의 미반납 대출 여부 체크
        cursor.execute("""
            SELECT 1 FROM borrowing
            WHERE u_id = %s AND is_returned = 0
        """, (user_id,))
        if cursor.fetchone():
            print(ERR_USER_BORROWED_CANNOT_DELETE)
            return

        # 3. 삭제 (연관 borrowing, rate는 ON DELETE CASCADE)
        cursor.execute("DELETE FROM user WHERE u_id = %s", (user_id,))

    print(MSG_USER_REMOVE)
