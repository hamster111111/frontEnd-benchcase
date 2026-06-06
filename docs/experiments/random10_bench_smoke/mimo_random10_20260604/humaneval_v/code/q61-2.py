def solution(m: int, n: int, k: int) -> list[int, int]:
    total = m * n
    k %= total
    row_idx = k // n
    offset = k % n
    if row_idx % 2 == 0:
        col_idx = offset
    else:
        col_idx = n - 1 - offset
    return [row_idx + 1, col_idx + 1]