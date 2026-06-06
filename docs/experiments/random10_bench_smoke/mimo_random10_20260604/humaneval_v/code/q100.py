from typing import Tuple
import math

def solution(coordinate: Tuple[int, int]) -> int:
    """
    Determines the color of the zone at the given coordinate.
    The colors follow an infinitely repeating pattern.

    Args:
        coordinate: A tuple (x, y) representing the coordinate point

    Returns:
        0 for white
        1 for black
        3 for boarder
    """
    x, y = coordinate
    dist_sq = x * x + y * y
    sqrt_dist = int(math.isqrt(dist_sq))
    
    # Check if the point lies exactly on a boundary circle (distance is integer)
    if sqrt_dist * sqrt_dist == dist_sq:
        return 3
    
    # Determine color based on floor of distance modulo 4
    k = sqrt_dist
    if k % 4 == 0 or k % 4 == 3:
        return 0  # white
    else:
        return 1  # black