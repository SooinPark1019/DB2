"""
유틸 함수들을 모아둔 파일
"""

def safe_mean(values):
    filtered = [v for v in values if v is not None]
    return round(sum(filtered)/len(filtered), 2) if filtered else None

def normalize(s: str) -> str:
    return s.lower()

def validate_length(value: str, min_len: int, max_len: int) -> bool:
    return min_len <= len(value) <= max_len

def to_positive_int(value: str) -> int | None:
    try:
        n = int(value)
        return n if n > 0 else None
    except ValueError:
        return None

def is_valid_age_limit(value: str) -> bool:
    try:
        n = int(value)
        return 0 <= n <= 19
    except ValueError:
        return False

def is_valid_rating(value: str) -> bool:
    try:
        n = int(value)
        return 1 <= n <= 5
    except ValueError:
        return False

def format_rating(rating: float | None) -> str:
    if rating is None:
        return 'None'
    return f"{round(rating + 1e-8, 2):.2f}".rstrip('0').rstrip('.') if '.' in f"{rating:.2f}" else f"{rating:.2f}"
    # (소수점 아래 0이면 안붙게)

def print_table(headers, rows):
    col_widths = [max(len(str(x)) for x in [h]+[row[i] for row in rows]) for i, h in enumerate(headers)]
    header_row = ' '.join(str(h).ljust(col_widths[i]) for i, h in enumerate(headers))
    print(header_row)
    print('-' * len(header_row))
    for row in rows:
        print(' '.join(str(x).ljust(col_widths[i]) for i, x in enumerate(row)))
