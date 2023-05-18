from typing import List


def inclusive_range(start: int, stop: int, step: int) -> List[int]:
    """
    Generates a list of integers within the specified range, including the 'stop' value if necessary.

    Args:
        start (int): The starting value of the range (inclusive).
        stop (int): The ending value of the range (inclusive).
        step (int): The difference between each consecutive value in the range.

    Returns:
        List[int]: A list of integers within the specified range, including the 'stop' value if necessary.

    Examples:
        >>> inclusive_range(3, 21, 5)
        [3, 8, 13, 18, 21]

        >>> inclusive_range(10, 20, 2)
        [10, 12, 14, 16, 18, 20]
    """
    range_list = list(range(start, stop, step))
    if range_list[-1] != stop:
        range_list.append(stop)
    
    return range_list
    