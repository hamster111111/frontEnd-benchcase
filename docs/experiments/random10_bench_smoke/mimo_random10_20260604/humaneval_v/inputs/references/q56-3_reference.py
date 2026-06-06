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

    # Traverse diagonals from bottom-right to top-left
    for d in range(2 * n - 1):
        if d < n:
            # Lower half including main diagonal
            for i in range(d + 1):
                if (n - 1 - i) >= 0 and (n - 1 - d + i) >= 0:
                    result.append(matrix[n - 1 - i][n - 1 - d + i])
        else:
            # Upper half excluding main diagonal
            for i in range(d - n + 1, n):
                if (n - 1 - i) >= 0 and (n - 1 - d + i) >= 0:
                    result.append(matrix[n - 1 - i][n - 1 - d + i])

    return result
