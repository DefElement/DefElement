"""Argument types."""
from abc import ABC, abstractmethod


class ArgType(ABC):
    """A type that can be the input or output of a function."""

    @abstractmethod
    def type(self, language: str) -> str:
        """Type in the given language."""

class NDArray(ArgType):
    """N-dimensional array."""

    def __init__(self, variable: str, dimension: int, shape: tuple[int | str, ...] | None, dtype: str):
        """Initialise."""
        self.variable = variable
        self.dimension = dimension
        self.dtype = dtype
        self.shape = shape

    def type(self, language: str) -> str:
        """Type in the given language."""
        match language:
            case "cpp":
                return f"mdspan<{self.dtype}, {self.dimension}>"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def initialise(self, language: str) -> str:
        """Initialise in the given language."""
        assert self.shape is not None
        match language:
            case "cpp":
                return "\n".join([
                    f"std::vector<{self.dtype}> {self.variable}_data(" + " * ".join(f"{i}" for i in self.shape) + ");",
                    f"std::array<std::size_t, {self.dimension}> {self.variable}_shape = {{" + ", ".join(f"{i}" for i in self.shape) + "};",
                    f"mdspan<{self.dtype}, {self.dimension}> {self.variable}({self.variable}_data.data(), {self.variable}_shape);"
                ])
            case _:
                raise ValueError(f"Unsupported language: {language}")


def ndarray(
    variable: str,
    dimension: int,
    shape: tuple[int | str, ...] | None = None,
    dtype: str = "double",
) -> ArgType:
    """Create an n-dimensional array."""
    return NDArray(variable, dimension, shape, dtype)


def array(
    variable: str,
    length: int | str | None = None,
    dtype: str = "double",
) -> ArgType:
    """Create a one-dimensional array."""
    return NDArray(variable, 1, None if length is None else (length, ), dtype)

