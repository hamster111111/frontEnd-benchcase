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
    sq = math.sqrt(x*x + y*y)
    if int(sq) == sq:
        return 3
    
    r_floor = math.floor(sq)
    if x > 0 and y > 0:
        quadrant = 1
    elif x < 0 and y > 0:
        quadrant = 2
    elif x < 0 and y < 0:
        quadrant = 3
    elif x > 0 and y < 0:
        quadrant = 4
    else:
        quadrant = 1
    
    if quadrant in [1, 3]:
        return 1 if (r_floor % 2 == 0) else 0
    else:
        return 0 if (r_floor % 2 == 0) else 1
