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

    def metadata_function_signature(self, language: str, inputs: str) -> str | None:
        """Get the signature of the function to generate metadata for this type."""
        return None

    def metadata_function_impl(self, language: str, function: str) -> str | None:
        """Get the signature of the function to generate metadata for this type."""
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

    def initialise(self, language: str, output: bool = False) -> str:
        """Initialise in the given language."""
        return ""

    def to_raw(self, lib, ffi, obj):
        """Convert python object to a raw C type."""
        return obj

    def from_raw(self, lib, ffi, obj):
        """Convert raw C object to a Python type."""
        return obj

    @property
    def in_out(self) -> bool:
        """Is this an in/out argument when used as an output?"""
        return False

    def empty(self, lib, ffi, inputs):
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
    def shape_type_name(self):
        return f"defelement_type_raw_{self.variable}_shape"

    @property
    def shape_function_name(self):
        return f"defelement_function_raw_{self.variable}_shape"

    @property
    def shape_variable_name(self):
        return f"defelement_raw_{self.variable}_shape"

    @property
    def raw_type_name(self):
        return f"defelement_type_raw_{self.variable}"

    @property
    def raw_variable_name(self):
        return f"defelement_raw_{self.variable}"

    @property
    def in_out(self) -> bool:
        """Is this an in/out argument when used as an output?"""
        return True

    def empty(self, lib, ffi, inputs):
        """Create an empty instance of this object to use as an in/out argument."""
        shape = getattr(lib, self.shape_function_name)(*inputs)
        return np.empty([getattr(shape, f"shape{i}") for i in range(self.dimension)])

    def metadata_function_signature(self, language: str, inputs: str) -> str | None:
        """Get the signature of the function to generate metadata for this type."""
        match language:
            case "cpp":
                return f"{self.shape_type_name} {self.shape_function_name}({inputs})"
            case _:
                return None

    def metadata_function_impl(self, language: str, function: str) -> str | None:
        """Get the signature of the function to generate metadata for this type."""
        out = ""
        if f"INIT {self.variable}" in function:
            out += function.split(f"INIT {self.variable}")[0]

        out += f"{self.shape_type_name} {self.shape_variable_name} = {{ "
        if self.shape is None:
            out += ", ".join(f".shape{i} = {self.raw_variable_name}.shape{i}" for i in range(self.dimension))
        else:
            out += ", ".join(f".shape{i} = (int){j}" for i, j in enumerate(self.shape))
        out += " };\n"
        out += f"return {self.shape_variable_name};"

        return out

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
                return f"{self.raw_type_name} {self.raw_variable_name}"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def function_output(self, language: str):
        """Output(s) from a function."""
        match language:
            case "cpp":
                return "\n".join([
                    f"{self.raw_type_name} {self.variable}_out = {{ " + ", ".join([
                        f".data = {self.raw_variable_name}.data()"] + [
                        f".shape{i} = {self.shape_variable_name}[{i}]" for i in range(self.dimension)
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
                    f"  {self.dtype}* data;",
                ] + [
                    f"  int shape{i};" for i in range(self.dimension)
                ] + [
                    f"}} {self.raw_type_name};",
                    f"typedef struct {self.shape_type_name} {{",
                ] + [
                    f"  int shape{i};" for i in range(self.dimension)
                ] + [
                    f"}} {self.shape_type_name};",
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

    def initialise(self, language: str, output: bool = False) -> str:
        """Initialise in the given language."""
        match language:
            case "cpp":
                lines = []
                line = f"std::array<int, {self.dimension}> {self.shape_variable_name} = {{"
                if self.shape is None:
                    line += ", ".join(f"{self.raw_variable_name}.shape{i}" for i in range(self.dimension))
                else:
                    line += ", ".join(f"(int){i}" for i in self.shape)
                line += "};"
                lines.append(line)
                if output:
                    assert self.shape is not None
                    lines += [
                        f"std::vector<{self.dtype}> {self.raw_variable_name}(" + " * ".join(f"{i}" for i in self.shape) + ");",
                        f"mdspan<{self.dtype}, {self.dimension}> {self.variable}({self.raw_variable_name}.data(), {self.shape_variable_name});",
                    ]
                else:
                    lines.append(
                        f"mdspan<{self.dtype}, {self.dimension}> {self.variable}({self.raw_variable_name}.data, {self.shape_variable_name});",
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


class Scalar(ArgType):
    """Scalar."""

    def __init__(self, variable: str, dtype: str):
        """Initialise."""
        self.variable = variable
        self.dtype = dtype

    def type(self, language: str):
        """Input(s) to a function."""
        match language:
            case "cpp":
                return self.dtype
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def function_input(self, language: str):
        """Input(s) to a function."""
        match language:
            case "cpp":
                return f"{self.dtype} {self.variable}"
            case _:
                raise ValueError(f"Unsupported language: {language}")

    def function_output(self, language: str):
        """Output(s) from a function."""
        match language:
            case "cpp":
                return f"return {self.variable};"
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


def int(
    variable: str,
) -> ArgType:
    """Create a one-dimensional array."""
    return Scalar(variable, "int")


def double(
    variable: str,
) -> ArgType:
    """Create a one-dimensional array."""
    return Scalar(variable, "double")
