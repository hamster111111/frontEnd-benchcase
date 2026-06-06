from typing import List

def solution(matrix: List[List[int]]) -> List[int]:
    """
    Traverses an n x n matrix according to a specified pattern.

    Parameters:
        matrix (List[List[int]]): An n x n integer matrix      

    Returns:
        List[int]: A list containing elements in the order of traversal
    """
    n = len(matrix)
    result = []
    # Iterate diagonals from bottom-right (k = 2n-2) to top-left (k = 0)
    for k in range(2 * n - 2, -1, -1):
        # For each diagonal, traverse from bottom to top (row index decreases)
        for r in range(n - 1, -1, -1):
            c = k - r
            if 0 <= c < n:
                result.append(matrix[r][c])
    return result