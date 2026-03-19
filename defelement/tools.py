"""DefElement tools."""

import typing

from numpy import float64
from numpy.typing import NDArray


def to_array(
    data: NDArray[float64] | list[typing.Any] | tuple[typing.Any, ...],
) -> float | NDArray[float64]:
    """Convert to an array."""
    import numpy as np

    if isinstance(data, (list, tuple)):
        return np.array([to_array(i) for i in data])
    return float(data)


def jsify(text):
    """Convert to a safe variable name for Javascript."""
    return text.replace(".", "_").replace("-", "_").replace("+", "p")
