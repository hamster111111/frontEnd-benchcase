def solution(matrix: list[list[int]]) -> list[int]:
    """
    Traverses a given matrix according to the snake pattern shown in the figure.
    
    Parameters:
        matrix (list[list[int]]): A 2D list (N x N matrix) containing integers that need to be traversed.
    
    Returns:
        list[int]: A list of integers representing the traversed elements.
    """
    result = []
    n = len(matrix)
    for i in range(n):
        if i % 2 == 0:
            # Even row index (0, 2, ...): Right to Left
            result.extend(matrix[i][::-1])
        else:
            # Odd row index (1, 3, ...): Left to Right
            result.extend(matrix[i])
    return result