"""Bempp-cl implementation."""

import typing

from defelement.implementations.core import Element, Implementation


class BemppClImplementation(Implementation):
    """Bempp-cl implementation."""

    @classmethod
    def format(
        cls, string: typing.Optional[str], params: typing.Dict[str, typing.Any]
    ) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        return f'"{string}"'

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import bempp_cl.api\ngrid = bempp_cl.api.shapes.regular_sphere(1)"

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

        Args:
            name: The name of this element for this implementation
            reference: The name of the reference cell
            degree: The degree of this example
            params: Additional parameters set in the .def file
            element: The element
            example: Example data

        Returns:
            Example code
        """
        return f'element = bempp_cl.api.function_space(grid, "{name}", {degree})'

    id = "bempp-cl"
    name = "Bempp-cl"
    url = "https://github.com/bempp/bempp-cl"
    install = "pip3 install numba scipy meshio\npip3 install bempp-cl"
