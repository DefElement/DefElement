"""DefElement tools."""

import typing
if typing.TYPE_CHECKING:
    from numpy import float64
    from numpy.typing import NDArray
    Array = NDArray[float64]
else:
    Array = typing.Any


def to_array(
    data: typing.Union[Array, typing.List[typing.Any], typing.Tuple[typing.Any, ...]]
) -> typing.Union[float, Array]:
    """Convert to an array."""
    import numpy as np

    if isinstance(data, (list, tuple)):
        return np.array([to_array(i) for i in data])
    return float(data)
