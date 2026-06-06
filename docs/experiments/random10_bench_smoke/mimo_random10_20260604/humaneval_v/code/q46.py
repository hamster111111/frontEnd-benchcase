def solution(s: str) -> str:
    """
    Modifies the input string according to a specified pattern.

    Parameters:
        s (str): The input string to modify.

    Returns:
        str: The modified string.
    """
    result_parts = []
    for idx, char in enumerate(s):
        if idx % 2 == 0:
            result_parts.append("abc")
        else:
            result_parts.append(char)
    return "".join(result_parts)