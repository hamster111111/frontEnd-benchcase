from typing import List

def solution(L: List[int]) -> List[int]:
    """
    Processes the input array according to a specific pattern.

    Parameters:
        L (List[int]): The source array to be processed       

    Returns:
        List[int]: The processed array
    """
    result = []
    temp = []
    
    for num in L:
        if num != 0:
            temp.append(num)
        else:
            if temp:
                result.append(max(temp))
                temp = []
    
    if temp:
        result.append(max(temp))
    
    return result