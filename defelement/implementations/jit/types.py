"""Types."""

class Type:
    """A type that can be the input or output of a function."""


class NDArray(Type):
    """N-dimensional array."""

    def __init__(self, variable: str, dimension: int):
        """Initialise."""
        self.variable = variable
        self.dimension = dimension


def ndarray(
    variable: str,
    dimension: int,
) -> Type:
    """Create an n-dimensional array."""
    return NDArray(variable, dimension)


def array(
    variable: str,
) -> Type:
    """Create a one-dimensional array."""
    return NDArray(variable, 1)

