from typing import List

def solution(colors: List[int], line_position: int) -> List[int]:
    """
    Transforms a 1D color array based on a given dashed line position.

    Args:
        colors (List[int]): A 1D array representing colors where:
            - 0 = white
            - 1 = light blue  
            - 2 = dark blue
        line_position (int): The position of the dashed line used for transformation

    Returns:
        List[int]: A new 1D array with transformed colors where:
            - 0 = white
            - 1 = light blue
            - 2 = dark blue
    """
    n = len(colors)
    left_part = colors[:line_position][::-1]
    right_part = colors[line_position:]
    
    max_length = max(len(left_part), len(right_part))
    result = []
    
    for i in range(max_length):
        left_value = left_part[i] if i < len(left_part) else 0
        right_value = right_part[i] if i < len(right_part) else 0
        merged_value = left_value + right_value
        result.append(min(merged_value, 2))  # Ensure the value does not exceed 2
    
    return result
