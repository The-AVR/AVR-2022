from typing import Tuple

from .calc import normalize_value


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
    norm_value = normalize_value(value, min_value, max_value)
    diff = [f - e for f, e in zip(max_color, min_color)]
    smear = [int(d * norm_value) for d in diff]
    return tuple(e + s for e, s in zip(min_color, smear))


def wrap_text(text: str, color: str) -> str:
    """
    Take a color, and wrap the text with a `span` element for that color.
    """
    return f"<span style='color:{color};'>{text}</span>"
