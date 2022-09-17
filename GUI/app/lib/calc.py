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
    return relative_value / value_range


def map_value(
    x: float, in_min: float, in_max: float, out_min: float, out_max: float
) -> float:
    return (x - in_min) * (out_max - out_min) / (in_max - in_min) + out_min
