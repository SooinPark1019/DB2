from db import db_cursor
from messages import *
from util import format_rating, print_table, to_positive_int

def recommend_popularity():
    user_id_input = input('User ID: ').strip()
    user_id = to_positive_int(user_id_input)
    if user_id is None:
        print(ERR_USER_NOT_EXIST.format(user_id_input))
        return

    with db_cursor(dictionary=True) as (conn, cursor):
        # 1. 회원 존재 여부 체크
        cursor.execute("SELECT u_age FROM user WHERE u_id = %s", (user_id,))
        row = cursor.fetchone()
        if not row:
            print(ERR_USER_NOT_EXIST.format(user_id))
            return
        user_age = row['u_age']

        # 2. 추천 가능한 DVD 목록
        # - 유저가 아직 평점을 남기지 않았고, 유저 나이 이상만, DVD 존재
        cursor.execute("""
            SELECT
                d.d_id, d.d_title, d.d_name, d.age_limit, d.cumul_rent_cnt, d.stock,
                AVG(r.rating) AS avg_rating
            FROM dvd d
            LEFT JOIN rate r ON d.d_id = r.d_id
            WHERE d.age_limit <= %s
              AND d.d_id NOT IN (SELECT d_id FROM rate WHERE u_id=%s)
            GROUP BY d.d_id, d.d_title, d.d_name, d.age_limit, d.cumul_rent_cnt, d.stock
        """, (user_age, user_id))

        candidates = cursor.fetchall()
        if not candidates:
            print(ERR_NO_RECOMMEND)
            return

        # 3. 최고 평점 DVD 구하기 (여러개면 id 가장 작은 것)
        best_rating = None
        best_dvd = None
        for row in candidates:
            rating = row['avg_rating']
            if rating is None:
                continue  # 평점 없는 건 넘겨도 됨
            if (best_rating is None or rating > best_rating or
                (rating == best_rating and row['d_id'] < best_dvd['d_id'])):
                best_rating = rating
                best_dvd = row

        # 4. 최고 누적 대출 DVD 구하기 (여러개면 id 가장 작은 것)
        best_rent_cnt = None
        most_rented_dvd = None
        for row in candidates:
            cnt = row['cumul_rent_cnt']
            if (best_rent_cnt is None or cnt > best_rent_cnt or
                (cnt == best_rent_cnt and row['d_id'] < most_rented_dvd['d_id'])):
                best_rent_cnt = cnt
                most_rented_dvd = row

        # 둘 중 하나라도 None이면 추천 불가
        if best_dvd is None and most_rented_dvd is None:
            print(ERR_NO_RECOMMEND)
            return

        # 5. 결과 출력
        headers = ['id', 'title', 'director', 'age_limit', 'criterion', 'stock']
        rows = []
        # 평점 기준 추천
        if best_dvd is not None:
            rows.append([
                best_dvd['d_id'],
                best_dvd['d_title'],
                best_dvd['d_name'],
                best_dvd['age_limit'],
                'avg.rating',
                best_dvd['stock'],
            ])
        # 누적 대출 기준 추천 (평점 DVD와 같으면 중복 출력 안 함)
        if most_rented_dvd is not None and (not best_dvd or most_rented_dvd['d_id'] != best_dvd['d_id']):
            rows.append([
                most_rented_dvd['d_id'],
                most_rented_dvd['d_title'],
                most_rented_dvd['d_name'],
                most_rented_dvd['age_limit'],
                'cumul_rent_cnt',
                most_rented_dvd['stock'],
            ])

        print('-' * 80)
        print_table(headers, rows)
        print('-' * 80)
