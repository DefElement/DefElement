"""Bempp-cl implementation."""

import typing

from defelement.implementations.core import Implementation, pypy_name
from defelement.element import Element


@pypi_name("bempp-cl", ["numba", "scipy", "meshio"])
class BemppClImplementation(Implementation):
    """Bempp-cl implementation."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
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
        """Generate code for a single example."""
        return f'element = bempp_cl.api.function_space(grid, "{name}", {degree})'

    id = "bempp-cl"
    name = "Bempp-cl"
    url = "https://github.com/bempp/bempp-cl"
