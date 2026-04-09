"""Argument types."""
from abc import ABC, abstractmethod
from itertools import product
import numpy as np
import ctypes


class ArgType(ABC):
    """A type that can be the input or output of a function."""

    def define_custom_type(self, language: str) -> str | None:
        """Definition of type to include if necessary."""
        return None

    def init_custom_type(self, language: str) -> str | None:
        """Initialise of custom type(s) to include if necessary."""
        return None

    @abstractmethod
    def type(self, language: str) -> str:
        """Type to use for function output."""

    @abstractmethod
    def function_input(self, language: str) -> str:
        """Input(s) to a function."""

    @abstractmethod
    def function_output(self, language: str) -> str:
        """Output(s) from a function."""

    @abstractmethod
    def initialise(self, language: str, indentation: int = 0) -> str:
        """Initialise in the given language."""

    @abstractmethod
    def to_raw(self, lib, ffi, obj):
        """Convert python object to a raw C type."""

    @abstractmethod
    def from_raw(self, lib, ffi, obj):
        """Convert raw C object to a Python type."""

    @property
    def in_out(self) -> bool:
        """Is this an in/out argument when used as an output?"""
        return False

    def empty(self, lib, ffi):
        """Create an empty instance of this object to use as an in/out argument."""
        raise NotImplmentedError("empty not implemented for this argument type.")


class NDArray(ArgType):
    """N-dimensional array."""

    def __init__(self, variable: str, dimension: int, shape: tuple[int | str, ...] | None, dtype: str):
        """Initialise."""
        self.variable = variable
        self.dimension = dimension
        self.dtype = dtype
        self.shape = shape

    @property
    def in_out(self) -> bool:
        """Is this an in/out argument when used as an output?"""
        return True

    def empty(self, lib, ffi):
        """Create an empty instance of this object to use as an in/out argument."""
        return np.empty([1, 1, 3])

    @property
    def raw_type_name(self):
        return f"defelement_type_raw_{self.variable}"

    @property
    def raw_type_variable_name(self):
        return f"defelement_raw_{self.variable}"

    def type(self, language: str):
        """Input(s) to a function."""
        match language:
            case "cpp":
                return f"{self.raw_type_name}"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def function_input(self, language: str):
        """Input(s) to a function."""
        match language:
            case "cpp":
                return f"{self.raw_type_name} {self.raw_type_variable_name}"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def function_output(self, language: str):
        """Output(s) from a function."""
        match language:
            case "cpp":
                return "\n".join([
                    f"{self.raw_type_name} {self.variable}_out = {{ " + ", ".join([
                        f".data = {self.raw_type_variable_name}.data()"] + [
                        f".shape{i} = {self.variable}_shape[{i}]" for i in range(self.dimension)
                    ]) + " };",
                    f"return {self.variable}_out;",
                ])
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def define_custom_type(self, language: str) -> str | None:
        """Definition of type to include if necessary."""
        match language:
            case "cpp":
                return "\n".join([
                    f"typedef struct {self.raw_type_name} {{",
                    f"  {self.dtype}* data;"] + [
                    f"  int shape{i};" for i in range(self.dimension)
                ] + [
                    f"}} {self.raw_type_name};",
                    f"typedef struct {self.raw_type_name}_metadata {{",
                    f"  int shape{i};" for i in range(self.dimension)
                ] + [
                    f"}} {self.raw_type_name}_metadata;",
                    f"{self.raw_type_name} new_{self.raw_type_name}({self.dtype}* data, " + ", ".join(f"int shape{i}" for i in range(self.dimension)) + ");",
                ])
            case _:
                return None

    def init_custom_type(self, language: str) -> str | None:
        """Initialise of custom type(s) to include if necessary."""
        match language:
            case "cpp":
                return "\n".join([
                    f"{self.raw_type_name} new_{self.raw_type_name}({self.dtype}* data, " + ", ".join(f"int shape{i}" for i in range(self.dimension)) + "){",
                    f"  {self.raw_type_name} out = {{ .data = data, " + ", ".join(f".shape{i} = shape{i}" for i in range(self.dimension)) + " };",
                    "  return out;",
                    "}",
                ])
            case _:
                return None

    def initialise(self, language: str, indentation: int = 0, output: bool = False) -> str:
        """Initialise in the given language."""
        tab = " " * indentation
        match language:
            case "cpp":
                lines = []
                if self.shape is None:
                    lines.append(
                        f"{tab}std::array<int, {self.dimension}> {self.variable}_shape = {{" + ", ".join(f"{self.raw_type_variable_name}.shape{i}" for i in range(self.dimension)) + "};",
                    )
                else:
                    lines.append(
                        f"{tab}std::array<int, {self.dimension}> {self.variable}_shape = {{" + ", ".join(f"(int){i}" for i in self.shape) + "};",
                    )
                if output:
                    assert self.shape is not None
                    lines += [
                        f"std::vector<{self.dtype}> {self.raw_type_variable_name}(" + " * ".join(f"{i}" for i in self.shape) + ");",
                        f"{tab}mdspan<{self.dtype}, {self.dimension}> {self.variable}({self.raw_type_variable_name}.data(), {self.variable}_shape);",
                    ]
                else:
                    lines.append(
                        f"{tab}mdspan<{self.dtype}, {self.dimension}> {self.variable}(static_cast<{self.dtype}*>({self.raw_type_variable_name}.data), {self.variable}_shape);",
                    )
                return "\n".join(lines)
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def to_raw(self, lib, ffi, obj):
        """Convert python object to a raw C type."""
        return getattr(lib, f"new_{self.raw_type_name}")(ffi.cast("double*", obj.ctypes.data), *obj.shape)

    def from_raw(self, lib, ffi, obj):
        """Convert raw C object to a Python type."""
        shape = [getattr(obj, f"shape{i}") for i in range(self.dimension)]
        out = np.empty(shape)
        i = 0
        for index in product(*[range(j) for j in shape]):
            out.__setitem__(index, obj.data[i])
            i += 1
        return out
        # return np.ctypeslib.as_array(obj.data, shape=[getattr(obj, f"shape{i}") for i in range(self.dimension)])


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

