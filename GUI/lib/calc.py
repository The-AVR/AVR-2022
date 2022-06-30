def constrain(value: float, min_value: float, max_value: float) -> float:
    """
    Bound a value within a given range
    """
    return min(max_value, max(min_value, value))

def normalize_value(value: float, min_value: float, max_value: float) -> float:
    """
    Bound and normalize a value within a given range
    """
    value = constrain(value, min_value, max_value)

    value_range = max_value - min_value
    relative_value = value - min_value
    norm_value = relative_value / value_range
    return norm_value
