"""Implementation template class and other functions."""

import re
import typing

if typing.TYPE_CHECKING:
    from numpy import float64
    from numpy.typing import NDArray

    from defelement.element import Element

    Array = NDArray[float64]
else:
    Array = typing.Any
    Element = typing.Any


class Implementation:
    """An implementation."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string.

        This function is passed the string and parameters set in a .def file for an
        implementation and should return the string to display on the element's page.

        This function must be implemented.

        Args:
            string: Implementation string as set in the .def file
            params: Additional parameters set in the .def file

        Returns:
            Formatted implementation string
        """
        raise NotImplementedError()

    @classmethod
    def example_import(cls) -> str:
        """Get code for imports to include at start of examples snippet.

        This function must be implemented.

        Returns:
            Python code for imports
        """
        raise NotImplementedError()

    @classmethod
    def single_example(
        cls,
        name: str,
        reference: str,
        degree: int,
        params: dict[str, str],
        element: Element,
        example: str,
    ) -> str:
        """Generate code for a single example.

        This function takes the element string and parameters (as set in the .def file)
        and the reference cell and degree for an example and should return a string of Python code
        that will create the example element.

        The additional inputs element and example may be needed in some more complex cases.

        This function must be implemented.

        Args:
            name: Implementation string as set in the .def file
            reference: The name of the reference cell
            degree: The degree of this example
            params: Additional parameters set in the .def file
            element: The DefElement element object
            example: Raw example data

        Returns:
            Example code
        """
        raise NotImplementedError()

    @classmethod
    def verify(
        cls,
        name: str,
        reference: str,
        degree: int,
        params: dict[str, str],
        element: Element,
        example: str,
    ) -> tuple[list[list[list[int]]], typing.Callable[[Array], Array]]:
        """Get information needed to run verification.

        Implementation of this function is optional, but it must be implemented for verification
        to be carried out. If this function is implemented, then the class variable `verification`
        should be set to `True` to activate verification.

        Args:
            name: Implementation string as set in the .def file
            reference: The name of the reference cell
            degree: The degree of this example
            params: Additional parameters set in the .def file
            element: The DefElement element object
            example: Raw example data

        Returns:
            This function returns two things:
            - A list of lists of lists that gives the degrees of freedom (DOFs) associated with
              each sub-entity. The entry `[i][j][k]` of this returned value is the `k`th dof that
              is associated with the `j`th sub-entity of dimension `i`.
            - A function thtat takes a set of points on the DefElement reference cell as input and
              returns the a Numpy array containing the values of the basis functions at every point.
              The entry `[i, j, k]` in this Numpy array is the `j`th component of the `k`th basis
              function evaluated at the `i`th point.
        """
        raise NotImplementedError()

    @classmethod
    def implemented(cls, element: Element) -> bool:
        """Check if an element is implemented.

        This can be used to overrule Element's implemented function.

        Implementation of this function is optional.

        Args:
            element: The element

        Returns:
            Example code
        """
        return True

    @classmethod
    def notes(cls, element: Element) -> list[str]:
        """Return a list of notes to include for the implementation of this element.

        Implementation of this function is optional.

        Args:
            element: Element data

        Returns:
            List of notes
        """
        return []

    @classmethod
    def references(cls, element: Element) -> list[dict[str, str]]:
        """Return a list of additional references to include for the implementation of this element.

        Implementation of this function is optional.

        Args:
            element: Element data

        Returns:
            List of references
        """
        return []

    @classmethod
    def examples(cls, element: Element) -> str:
        """Generate code for all examples.

        This function should not be overridden in subclasses.

        Args:
            element: The element

        Returns:
            Example code
        """
        code = cls.example_import()
        assert cls.id is not None
        for eg in element.examples:
            reference, defelement_degree, variant, kwargs = parse_example(eg)
            try:
                name, degree, params = element.get_implementation_string(
                    cls.id, reference, defelement_degree, variant
                )
            except NotImplementedError:
                continue
            assert degree is not None
            code += "\n\n"
            code = "# Create "
            if variant is None:
                code += element.name
            else:
                code += element.name_with_variant(variant)
            code += f" degree {degree} on a {reference}\n"
            code += cls.single_example(name, reference, degree, params, element, eg)
        return code

    # Unique identifier used in implementation section of .def files
    id: str | None = None
    # The name of the implementation
    name: str | None = None
    # Snippet to install the implementation
    install: str | None = None
    # URL of source of implementation (eg GitHub link)
    url: str | None = None
    # Set to true if this implementation should be verified
    verification = False


class VariantNotImplemented(NotImplementedError):
    """Error for variants that are not implemented."""


class DegreeNotImplemented(NotImplementedError):
    """Error for degrees that are not implemented."""


class NotImplementedOnReference(NotImplementedError):
    """Error for element not implemented on a reference cell."""


ValueType = typing.Union[int, str, list["ValueType"]]


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
) -> tuple[str, int, str | None, dict[str, int | str | list[ValueType]]]:
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
