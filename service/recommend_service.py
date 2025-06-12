from db import db_cursor
from messages import *
from util import format_rating, print_table, to_positive_int, print_table
import math

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


def recommend_user_based():
    user_id_input = input('User ID: ').strip()
    try:
        user_id = int(user_id_input)
    except ValueError:
        print(ERR_USER_NOT_EXIST.format(user_id_input))
        return

    # 1. 유저 존재 확인 및 나이 확인
    with db_cursor(dictionary=True) as (conn, cursor):
        cursor.execute("SELECT u_id, u_age FROM user WHERE u_id=%s", (user_id,))
        urow = cursor.fetchone()
        if not urow:
            print(ERR_USER_NOT_EXIST.format(user_id))
            return
        u_age = urow['u_age']

        # 2. 모든 DVD/유저 정보와 평점, 나이제한 불러오기
        cursor.execute("""
            SELECT d.d_id, d.d_title, d.d_name, d.age_limit, d.stock,
                   u.u_id, u.u_name,
                   r.rating
            FROM dvd d
            CROSS JOIN user u
            LEFT JOIN rate r ON d.d_id = r.d_id AND u.u_id = r.u_id
            WHERE d.age_limit <= %s
            ORDER BY d.d_id, u.u_id
        """, (u_age,))
        records = cursor.fetchall()

    # 3. 유저ID, DVDID, 평점, DVD 메타정보 매핑
    user_ids = sorted({r['u_id'] for r in records})
    dvd_ids = sorted({r['d_id'] for r in records})
    uid2idx = {uid: i for i, uid in enumerate(user_ids)}
    did2idx = {did: i for i, did in enumerate(dvd_ids)}
    idx2uid = {i: uid for uid, i in uid2idx.items()}
    idx2did = {i: did for did, i in did2idx.items()}

    # 평점 행렬 N x M (N=유저수, M=DVD수)
    n, m = len(user_ids), len(dvd_ids)
    ratings = [[None] * m for _ in range(n)]
    dvd_meta = {}
    for r in records:
        i = uid2idx[r['u_id']]
        j = did2idx[r['d_id']]
        ratings[i][j] = r['rating']
        # dvd 메타데이터 저장(나중 출력용)
        if j not in dvd_meta:
            dvd_meta[j] = {
                'd_id': r['d_id'],
                'd_title': r['d_title'],
                'd_name': r['d_name'],
                'age_limit': r['age_limit'],
                'stock': r['stock'],
            }

    # 4. 임시 평점 대입: 각 DVD의 유효평점의 평균을 None인 곳에 대입
    dvd_avgs = []
    for j in range(m):
        vals = [ratings[i][j] for i in range(n) if ratings[i][j] is not None]
        avg = round(sum(vals)/len(vals), 2) if vals else None
        dvd_avgs.append(avg)
        for i in range(n):
            if ratings[i][j] is None:
                ratings[i][j] = avg

    # 5. 코사인 유사도 행렬
    def cosine_sim(u, v):
        # u, v: 두 개의 벡터 (리스트)
        num = sum(a*b for a, b in zip(u, v))
        denom1 = math.sqrt(sum(a*a for a in u))
        denom2 = math.sqrt(sum(b*b for b in v))
        if denom1 == 0 or denom2 == 0:
            return 0.0
        return num / (denom1 * denom2)
    # N x N 유사도
    sims = [[0.0]*n for _ in range(n)]
    for i in range(n):
        for j in range(m):
            if ratings[i][j] is None:
                ratings[i][j] = dvd_avgs[j] if dvd_avgs[j] is not None else 0

    # 6. 추천 대상 DVD 후보 선정 (해당 유저가 평점 남기지 않은, age_limit 만족, 아직 평점 안 남긴 것)
    user_idx = uid2idx[user_id]
    rec_candidates = []
    for j in range(m):
        # 실제로 평점을 남긴 적 없는 DVD만 후보
        # "records"에서 user_id와 dvd_id로 평점을 직접 조회
        orig_rating = None
        for r in records:
            if r['u_id'] == user_id and r['d_id'] == idx2did[j]:
                orig_rating = r['rating']
                break
        if orig_rating is None:
            # 후보: 이 DVD에 대해 아직 평점 안 남김
            rec_candidates.append(j)

    if not rec_candidates:
        print(ERR_NO_RECOMMEND)
        return

    # 7. 각 후보 DVD에 대해 예상 평점 계산 (가중평균)
    pred_scores = []
    for j in rec_candidates:
        num = 0
        denom = 0
        for i in range(n):
            if i == user_idx:
                continue
            weight = sims[user_idx][i]
            rating = ratings[i][j]
            if rating is not None:
                num += weight * rating
                denom += abs(weight)
        if denom == 0:
            pred = 0
        else:
            pred = num / denom
        pred_scores.append((pred, j))

    # 8. 최고 예상 평점 DVD 찾기 (동률 시 ID 오름차순)
    pred_scores.sort(key=lambda x: (-x[0], dvd_meta[x[1]]['d_id']))
    top_pred, top_j = pred_scores[0]

    # 9. DVD 정보 출력
    # DVD ID, 제목, 감독, 나이 제한, 예상 평점, (참고: 실제 평균 평점)
    headers = ['id', 'title', 'director', 'age_limit', 'pred.rating', 'avg.rating', 'stock']
    rows = []
    meta = dvd_meta[top_j]
    rows.append([
        meta['d_id'],
        meta['d_title'],
        meta['d_name'],
        meta['age_limit'],
        format_rating(top_pred),
        format_rating(dvd_avgs[top_j]) if dvd_avgs[top_j] is not None else 'None',
        meta['stock']
    ])
    print('-'*80)
    print_table(headers, rows)
    print('-'*80)