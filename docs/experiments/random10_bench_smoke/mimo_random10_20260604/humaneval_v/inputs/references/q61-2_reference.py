def solution(m: int, n: int, k: int) -> list[int, int]:        
    """
    Given an m×n matrix, determine the coordinates after k steps, starting from position (1,1) (top-left corner).
    Each step can only move to an adjacent cell following a specific movement pattern.

    Parameters:
        m (int): Number of rows in the matrix.
        n (int): Number of columns in the matrix.
        k (int): Number of steps to move.

    Returns:
        list[int, int]: Final coordinates [row, column] after k steps.
    """
    if k < m:
        return [k + 1, 1]
    k -= (m - 1)
    i = m - 1   
    j = 0
    direct_status = "right"
    while k > 0:
        if direct_status == "right":
            j += 1
            if  j == n - 1 and i != 0 :
                direct_status = "up"
            
        elif direct_status == "up":
            i -= 1
            if j == 1:
                direct_status = "right"
            elif j == n - 1:
                direct_status = "left"
            else:
                assert False
        elif direct_status == "left":
            j -= 1
            if j == 1 and i != 0:
                direct_status = "up"
        k -= 1
    return [i + 1, j + 1]     
            
