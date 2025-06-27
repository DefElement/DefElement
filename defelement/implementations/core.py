"""Implementation template class and other functions."""

import re
import typing
from abc import ABC, abstractmethod

if typing.TYPE_CHECKING:
    from numpy import float64
    from numpy.typing import NDArray

    from defelement.element import Element

    Array = NDArray[float64]
else:
    Array = typing.Any
    Element = typing.Any


class Implementation(ABC):
    """An implementation."""

    @staticmethod
    @abstractmethod
    def format(
        string: typing.Optional[str], params: typing.Dict[str, typing.Any]
    ) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """

    @staticmethod
    @abstractmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """

    @staticmethod
    def verify(
        element: Element, example: str
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[int]]], typing.Callable[[Array], Array]
    ]:
        """Get verification data.

        Args:
            element: Element data
            example: Example data

        Returns:
            List of entity dofs, and tabulation function
        """
        raise NotImplementedError()

    @staticmethod
    def notes(element: Element) -> typing.List[str]:
        """Return a list of notes to include for the implementation of this element.

        Args:
            element: Element data

        Returns:
            List of notes
        """
        return []

    @staticmethod
    def references(element: Element) -> typing.List[typing.Dict[str, str]]:
        """Return a list of additional references to include for the implementation of this element.

        Args:
            element: Element data

        Returns:
            List of references
        """
        return []

    # Unique identifier used in implementation section of .def files
    id: typing.Optional[str] = None
    # The name of the implementation
    name: typing.Optional[str] = None
    # Snippet to install the implementation
    install: typing.Optional[str] = None
    # URL of source of implementation (eg GitHub link)
    url: typing.Optional[str] = None
    # Set to true if this implementation should be verified
    verification = False


class VariantNotImplemented(NotImplementedError):
    """Error for variants that are not implemented."""


class DegreeNotImplemented(NotImplementedError):
    """Error for degrees that are not implemented."""


class NotImplementedOnReference(NotImplementedError):
    """Error for element not implemented on a reference cell."""


ValueType = typing.Union[int, str, typing.List["ValueType"]]


def _parse_value(v: str) -> ValueType:
    """Parse a string.

    Args:
        v: String

    Returns:
        Parsed string
    """
    v = v.strip()
    if v[0] == "[" and v[-1] == "]":
        return [_parse_value(i) for i in v[1:-1].split(";")]
    if re.match(r"[0-9]+$", v):
        return int(v)
    return v


def parse_example(
    e: str,
) -> typing.Tuple[
    str,
    int,
    typing.Optional[str],
    typing.Dict[str, typing.Union[int, str, typing.List[ValueType]]],
]:
    """Parse an example.

    Args:
        e: The example

    Returns:
        Parsed example information
    """
    if " {" in e:
        e, rest = e.split(" {")
        rest = rest.split("}")[0]
        while re.search(r"\[([^\]]*),", rest):
            rest = re.sub(r"\[([^\]]*),", r"[\1;", rest)
        kwargs = {}
        for i in rest.split(","):
            key, value = i.split("=")
            kwargs[key] = _parse_value(value)
    else:
        kwargs = {}
    s = e.split(",")
    if len(s) == 3:
        ref, degree, variant = s
    else:
        ref, degree = e.split(",")
        variant = None
    return ref, int(degree), variant, kwargs
