from typing import List

def solution(l: List[int], swap_locations: List[int]) -> List[int]:
    """
    Modifies a list by swapping elements according to the specified swap locations.

    Parameters:
        l (List[int]): The input list to be modified
        swap_locations (List[int]): A list of indices indicating where elements should be swapped

    Returns:
        List[int]: The modified list after performing the swaps.
    """
    for loc in swap_locations:
        l = l[:loc][::-1] + l[loc:]
        
    return l
