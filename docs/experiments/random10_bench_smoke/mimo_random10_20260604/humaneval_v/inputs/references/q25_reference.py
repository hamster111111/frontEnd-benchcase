from typing import Dict, List, Tuple

def solution(rectangles: Dict[int, List[Tuple[int, int]]], rectangle_id: int) -> int:    
    """
    Calculate the trimmed area of a specified rectangle within a grid.

    Args:
        rectangles: A dictionary mapping rectangle IDs (int) to their corner coordinates.
                   Each value is a list containing two (column, row) tuples representing 
                   the bottom-left and top-right corners respectively.
                   Example: {1: [(0, 0), (2, 2)], 2: [(2, 0), (4, 2)]}
        rectangle_id: The ID of the target rectangle to calculate the trimmed area for.  

    Returns:
        The trimmed area of the specified rectangle.
    """
    # Sort rectangles by their ID (lower ID = higher priority)
    sorted_rectangles = sorted(rectangles.items(), key=lambda x: x[0])

    # Initialize a 3x7 grid to track coverage
    grid = [[0] * 7 for _ in range(3)]

    # Fill the grid based on rectangle priority
    for rect_id, coords in sorted_rectangles:
        bottom_left, top_right = coords
        x1, y1 = bottom_left
        x2, y2 = top_right
        for x in range(x1, x2):
            for y in range(y1, y2):
                # Only fill the cell if it hasn't been covered by a higher-priority rectangle
                if grid[y][x] == 0:
                    grid[y][x] = rect_id

    # Calculate the trimmed area for the given rectangle_id
    trimmed_area = sum(1 for y in range(3) for x in range(7) if grid[y][x] == rectangle_id)

    return trimmed_area
