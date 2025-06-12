from db import db_cursor
from messages import *
from util import to_positive_int, is_valid_rating
from datetime import datetime

def checkout_DVD():
    DVD_id = input('DVD ID: ').strip()
    user_id = input('User ID: ').strip()

    dvd_id = to_positive_int(DVD_id)
    u_id = to_positive_int(user_id)
    if dvd_id is None:
        print(ERR_DVD_NOT_EXIST.format(DVD_id))
        return
    if u_id is None:
        print(ERR_USER_NOT_EXIST.format(user_id))
        return

    with db_cursor() as (conn, cursor):
        # 1. DVD, USER 존재 여부 체크
        cursor.execute("SELECT d_id, age_limit, stock FROM dvd WHERE d_id=%s", (dvd_id,))
        dvd_row = cursor.fetchone()
        if not dvd_row:
            print(ERR_DVD_NOT_EXIST.format(dvd_id))
            return

        cursor.execute("SELECT u_id, u_age, overdue_score, penalty_left FROM user WHERE u_id=%s", (u_id,))
        user_row = cursor.fetchone()
        if not user_row:
            print(ERR_USER_NOT_EXIST.format(u_id))
            return

        # 2. 회원이 대출 중인 DVD 수 체크 (is_returned=0)
        cursor.execute("""
            SELECT COUNT(*) FROM borrowing
            WHERE u_id=%s AND is_returned=0
        """, (u_id,))
        borrow_cnt = cursor.fetchone()[0]
        if borrow_cnt >= 2:
            print(ERR_USER_BORROW_LIMIT.format(u_id))
            return

        # 3. 나이 제한 체크
        if user_row[1] < dvd_row[1]:
            print(ERR_USER_AGE_LIMIT.format(u_id))
            return

        # 4. 재고 체크
        if dvd_row[2] <= 0:
            print(ERR_DVD_OUT_OF_STOCK)
            return

        # 5. 현재 해당 DVD를 대출 중인 모든 회원의 연체 점수 1 증가
        cursor.execute("""
            SELECT u_id FROM borrowing
            WHERE d_id=%s AND is_returned=0
        """, (dvd_id,))
        borrowed_users = cursor.fetchall()
        for (borrower_id,) in borrowed_users:
            cursor.execute("""
                UPDATE user
                SET overdue_score = overdue_score + 1
                WHERE u_id = %s
            """, (borrower_id,))

        # 6. 해당 회원이 대출 제한 상태라면: 제한 메시지 + 남은 penalty_left 1 감소
        overdue_score = user_row[2]
        penalty_left = user_row[3]
        if penalty_left > 0:
            # 남은 패널티 횟수 차감
            cursor.execute("""
                UPDATE user SET penalty_left = penalty_left - 1 WHERE u_id=%s
            """, (u_id,))
            cursor.execute("SELECT penalty_left FROM user WHERE u_id=%s", (u_id,))
            remain = cursor.fetchone()[0]
            print(ERR_USER_RESTRICTED.format(u_id, remain))
            # 패널티 해제 조건 체크
            if remain == 0:
                cursor.execute("""
                    UPDATE user SET overdue_score=0 WHERE u_id=%s
                """, (u_id,))
            return
        elif overdue_score >= 5:
            # 패널티 진입: 제한 2회 부여, 대출 실패
            cursor.execute("""
                UPDATE user SET penalty_left = 2 WHERE u_id=%s
            """, (u_id,))
            print(ERR_USER_RESTRICTED.format(u_id, 2))
            return

        # 7. DVD 대출 등록: borrowing INSERT, 재고-1, DVD 누적대출+1
        now = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        cursor.execute("""
            INSERT INTO borrowing (d_id, u_id, borrowed_at, is_returned)
            VALUES (%s, %s, %s, 0)
        """, (dvd_id, u_id, now))
        cursor.execute("""
            UPDATE dvd SET stock = stock - 1, cumul_rent_cnt = cumul_rent_cnt + 1 WHERE d_id=%s
        """, (dvd_id,))
        print(MSG_DVD_CHECKOUT)

def return_and_rate_DVD():
    DVD_id = input('DVD ID: ').strip()
    user_id = input('User ID: ').strip()
    rating = input('Rating (1~5): ').strip()

    dvd_id = to_positive_int(DVD_id)
    u_id = to_positive_int(user_id)
    if dvd_id is None:
        print(ERR_DVD_NOT_EXIST.format(DVD_id))
        return
    if u_id is None:
        print(ERR_USER_NOT_EXIST.format(user_id))
        return
    if not is_valid_rating(rating):
        print(ERR_RATING_RANGE)
        return
    rating = int(rating)

    with db_cursor() as (conn, cursor):
        # 1. DVD 존재 여부
        cursor.execute("SELECT 1 FROM dvd WHERE d_id=%s", (dvd_id,))
        if not cursor.fetchone():
            print(ERR_DVD_NOT_EXIST.format(dvd_id))
            return

        # 2. 유저 존재 여부
        cursor.execute("SELECT 1 FROM user WHERE u_id=%s", (u_id,))
        if not cursor.fetchone():
            print(ERR_USER_NOT_EXIST.format(u_id))
            return

        # 3. 해당 DVD를 해당 회원이 빌렸는지 (is_returned = 0)
        cursor.execute("""
            SELECT b_id FROM borrowing
            WHERE d_id=%s AND u_id=%s AND is_returned=0
        """, (dvd_id, u_id))
        b_row = cursor.fetchone()
        if not b_row:
            print(ERR_NOT_BORROWED)
            return

        # 4. borrowing 반납처리 (is_returned=1, returned_at=NOW)
        cursor.execute("""
            UPDATE borrowing
            SET is_returned=1, returned_at=NOW()
            WHERE b_id=%s
        """, (b_row[0],))

        # 5. dvd 재고 +1
        cursor.execute("""
            UPDATE dvd SET stock = stock + 1 WHERE d_id=%s
        """, (dvd_id,))

        # 6. 평점 등록 (이미 있으면 UPDATE, 없으면 INSERT)
        cursor.execute("""
            SELECT 1 FROM rate WHERE d_id=%s AND u_id=%s
        """, (dvd_id, u_id))
        if cursor.fetchone():
            cursor.execute("""
                UPDATE rate SET rating=%s WHERE d_id=%s AND u_id=%s
            """, (rating, dvd_id, u_id))
        else:
            cursor.execute("""
                INSERT INTO rate (d_id, u_id, rating) VALUES (%s, %s, %s)
            """, (dvd_id, u_id, rating))

    print(MSG_DVD_RETURNED_RATED)