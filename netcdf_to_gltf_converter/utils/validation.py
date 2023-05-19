def in_range(value: float, lower_bound: float, upper_bound: float) -> bool:
    """Determine whether the a value is in the specified range (inclusive).

    Args:
        value (float): The value to check.
        lower_bound (float): The lower bound of the range (inclusive).
        upper_bound (float): The upper bound of the range (inclusive).

    Returns:
        bool: A boolean indicating whether the value is in range.
    """
    return lower_bound <= value <= upper_bound
