"""Argument types."""
from abc import ABC, abstractmethod


class ArgType(ABC):
    """A type that can be the input or output of a function."""

    @abstractmethod
    def type(self, language: str) -> str:
        """Type in the given language."""

    @abstractmethod
    def function_input(self, language: str) -> str:
        """Input(s) to a function."""

    @abstractmethod
    def function_output(self, language: str) -> str:
        """Output(s) from a function."""

    @abstractmethod
    def initialise(self, language: str) -> str:
        """Initialise in the given language."""


class NDArray(ArgType):
    """N-dimensional array."""

    def __init__(self, variable: str, dimension: int, shape: tuple[int | str, ...] | None, dtype: str):
        """Initialise."""
        self.variable = variable
        self.dimension = dimension
        self.dtype = dtype
        self.shape = shape

    def function_input(self, language: str):
        """Input(s) to a function."""
        match language:
            case "cpp":
                return f"{self.dtype}* {self.variable}_data, " + ", ".join([
                    f"int {self.variable}_shape{i}" for i in range(self.dimension)
                ])
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def function_output(self, language: str):
        """Output(s) from a function."""
        match language:
            case "cpp":
                return f"{{{self.variable}_data.data(), " + ", ".join([
                    f"{self.variable}.extent({i})" for i in range(self.dimension)
                ]) + "}"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def type(self, language: str) -> str:
        """Type in the given language."""
        match language:
            case "cpp":
                return f"std::tuple<{self.dtype}*, " + ", ".join(["int"] * self.dimension) + ">"
                return f"mdspan<{self.dtype}, {self.dimension}>"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def initialise(self, language: str) -> str:
        """Initialise in the given language."""
        match language:
            case "cpp":
                if self.shape is None:
                    return "\n".join([
                        f"std::array<int, {self.dimension}> {self.variable}_shape = {{" + ", ".join(f"{self.variable}_shape{i}" for i in range(self.dimension)) + "};",
                        f"mdspan<{self.dtype}, {self.dimension}> {self.variable}({self.variable}_data, {self.variable}_shape);"
                    ])
                else:
                    return "\n".join([
                        f"std::vector<{self.dtype}> {self.variable}_data(" + " * ".join(f"{i}" for i in self.shape) + ");",
                        f"std::array<int, {self.dimension}> {self.variable}_shape = {{" + ", ".join(f"{i}" for i in self.shape) + "};",
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

