from typing import Tuple


def smear_color(
    min_color: Tuple[int, int, int],
    max_color: Tuple[int, int, int],
    value: float,
    min_value: float,
    max_value: float,
) -> Tuple[int, int, int]:
    """
    Smear a color between two colors based on a value.
    """
    value = max(min_value, value)
    value = min(max_value, value)

    value_range = max_value - min_value
    relative_value = value - min_value
    norm_value = relative_value / value_range

    diff = [f - e for f, e in zip(max_color, min_color)]
    smear = [int(d * norm_value) for d in diff]
    return tuple(e + s for e, s in zip(min_color, smear))