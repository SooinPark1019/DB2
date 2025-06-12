import csv
from db import db_cursor
from messages import *
from util import to_positive_int, is_valid_age_limit, is_valid_rating, format_rating, print_table, validate_length

DATA_PATH = "data.csv"

def initialize_database():
    """
    1. 기존 테이블 DROP
    2. 테이블 CREATE
    3. data.csv 읽어서 데이터 적재 (재고 2로 초기화)
    4. 성공 메시지 출력
    """
    with db_cursor() as (conn, cursor):
        # 1. DROP TABLES IF EXISTS
        cursor.execute("DROP TABLE IF EXISTS borrowing")
        cursor.execute("DROP TABLE IF EXISTS rate")
        cursor.execute("DROP TABLE IF EXISTS user")
        cursor.execute("DROP TABLE IF EXISTS dvd")
        
        # 2. CREATE TABLES
        cursor.execute("""
        CREATE TABLE dvd (
            d_id INT PRIMARY KEY AUTO_INCREMENT,
            d_title VARCHAR(50) NOT NULL,
            d_name VARCHAR(50) NOT NULL,
            age_limit INT NOT NULL,
            stock INT NOT NULL DEFAULT 2,
            cumul_rent_cnt INT NOT NULL DEFAULT 0,
            UNIQUE KEY (d_title, d_name)
        )
        """)
        cursor.execute("""
        CREATE TABLE user (
            u_id INT PRIMARY KEY AUTO_INCREMENT,
            u_name VARCHAR(30) NOT NULL,
            u_age INT NOT NULL,
            overdue_score INT NOT NULL DEFAULT 0,
            penalty_left INT NOT NULL DEFAULT 0
        )
        """)
        cursor.execute("""
        CREATE TABLE rate (
            d_id INT NOT NULL,
            u_id INT NOT NULL,
            rating INT NOT NULL,
            PRIMARY KEY (d_id, u_id),
            FOREIGN KEY (d_id) REFERENCES dvd(d_id) ON DELETE CASCADE,
            FOREIGN KEY (u_id) REFERENCES user(u_id) ON DELETE CASCADE
        )
        """)
        cursor.execute("""
        CREATE TABLE borrowing (
            b_id INT PRIMARY KEY AUTO_INCREMENT,
            d_id INT NOT NULL,
            u_id INT NOT NULL,
            borrowed_at DATETIME NOT NULL,
            returned_at DATETIME,
            is_returned BOOL NOT NULL DEFAULT 0,
            FOREIGN KEY (d_id) REFERENCES dvd(d_id) ON DELETE CASCADE,
            FOREIGN KEY (u_id) REFERENCES user(u_id) ON DELETE CASCADE
        )
        """)
        
        # 3. data.csv를 읽어 dvd/user/rate 데이터 삽입
        dvds = {}
        users = {}
        dvd_id_map = {}
        user_id_map = {}

        with open(DATA_PATH, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            # print("DictReader fieldnames:", reader.fieldnames)
            for row in reader:
                # DVD 데이터
                d_id = int(row['d_id'])
                d_title = row['d_title']
                d_name = row['d_name']
                age_limit = int(row['age_limit'])
                # 회원 데이터
                u_id = int(row['u_id'])
                u_name = row['u_name']
                u_age = int(row['u_age'])
                # 평점
                rating = int(row['rating'])
                # dvd/user dict에 없으면 추가
                # print("d_title :", d_title, "d_name :", d_name, "u_name :", u_name, "u_age :", u_age, "rating :", rating)
                if d_id not in dvds:
                    dvds[d_id] = (d_title, d_name, age_limit)
                if u_id not in users:
                    users[u_id] = (u_name, u_age)

        # DVD 테이블 삽입 (순서대로 d_id 보장 위해)
        for d_id in sorted(dvds.keys()):
            d_title, d_name, age_limit = dvds[d_id]
            # print("d_title :", d_title, "d_name :", d_name)
            cursor.execute(
                "INSERT INTO dvd (d_title, d_name, age_limit, stock, cumul_rent_cnt) VALUES (%s, %s, %s, 2, 0)",
                (d_title, d_name, age_limit)
            )
            # AUTO_INCREMENT된 실제 PK 저장
            dvd_id_map[d_id] = cursor.lastrowid

        # User 테이블 삽입
        for u_id in sorted(users.keys()):
            u_name, u_age = users[u_id]
            cursor.execute(
                "INSERT INTO user (u_name, u_age, overdue_score, penalty_left) VALUES (%s, %s, 0, 0)",
                (u_name, u_age)
            )
            user_id_map[u_id] = cursor.lastrowid

        rate_map = {}

        with open(DATA_PATH, encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                old_did = int(row['d_id'])
                old_uid = int(row['u_id'])
                rating = int(row['rating'])
                rate_map[(old_did, old_uid)] = rating

        for (old_did, old_uid), rating in rate_map.items():
            cursor.execute(
                "INSERT INTO rate (d_id, u_id, rating) VALUES (%s, %s, %s)",
                (dvd_id_map[old_did], user_id_map[old_uid], rating)
            )

    print(MSG_DB_INIT)

def print_DVDs():
    """
    모든 DVD 정보를 포맷에 맞게 출력
    """
    headers = ['id', 'title', 'director', 'age_limit', 'avg.rating', 'cumul_rent_cnt', 'stock']
    rows = []

    with db_cursor(dictionary=True) as (conn, cursor):
        # DVD 정보 + 누적 대출 횟수, 재고 + 평균 평점 조인
        cursor.execute("""
            SELECT
                d.d_id,
                d.d_title,
                d.d_name,
                d.age_limit,
                d.cumul_rent_cnt,
                d.stock,
                AVG(r.rating) AS avg_rating
            FROM dvd d
            LEFT JOIN rate r ON d.d_id = r.d_id
            GROUP BY d.d_id, d.d_title, d.d_name, d.age_limit, d.cumul_rent_cnt, d.stock
            ORDER BY d.d_id
        """)
        for row in cursor.fetchall():
            avg_rating = row['avg_rating']
            avg_rating_str = format_rating(avg_rating) if avg_rating is not None else 'None'
            rows.append([
                row['d_id'],
                row['d_title'],
                row['d_name'],
                row['age_limit'],
                avg_rating_str,
                row['cumul_rent_cnt'],
                row['stock'],
            ])

    # 출력 포맷
    print('-' * 80)
    print_table(headers, rows)
    print('-' * 80)

def insert_DVD():
    title = input('DVD title: ').strip()
    director = input('DVD director: ').strip()
    age_limit = input('Age limit: ').strip()

    # 1. 제목 길이 체크
    if not validate_length(title, 1, 50):
        print(ERR_TITLE_LENGTH)
        return

    # 2. 감독명 길이 체크
    if not validate_length(director, 1, 30):
        print(ERR_DIRECTOR_LENGTH)
        return

    # 3. 나이제한 숫자/범위 체크
    if not is_valid_age_limit(age_limit):
        print(ERR_AGE_LIMIT)
        return
    age_limit = int(age_limit)

    # 4. (제목, 감독) 중복 체크
    with db_cursor() as (conn, cursor):
        cursor.execute(
            "SELECT 1 FROM dvd WHERE d_title=%s AND d_name=%s",
            (title, director)
        )
        if cursor.fetchone():
            print(ERR_DVD_EXISTS.format(title, director))
            return

        # 5. INSERT
        cursor.execute(
            "INSERT INTO dvd (d_title, d_name, age_limit, stock, cumul_rent_cnt) VALUES (%s, %s, %s, 2, 0)",
            (title, director, age_limit)
        )
        # 커밋은 context manager가 해줄 것

    print(MSG_DVD_INSERT)