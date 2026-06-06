from typing import List

def solution(L: List[int]) -> List[int]:
    result = []
    current_group = []
    for num in L:
        if num != 0:
            current_group.append(num)
        else:
            if current_group:
                result.append(max(current_group))
                current_group = []
    if current_group:
        result.append(max(current_group))
    return result