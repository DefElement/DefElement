"""Symfem implementation."""

import typing

from symfem.finite_element import FiniteElement

from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
    parse_example,
    pypi_name,
)
from defelement.tools import to_array


def symfem_create_element(element: Element, example: str) -> FiniteElement:
    """Create a Symfem element.

    Args:
        element: Element info
        example: The example

    Returns:
        Symfem element
    """
    import symfem

    ref, defelement_deg, variant, kwargs = parse_example(example)
    symfem_name, deg, params = element.get_implementation_string(
        "symfem", ref, defelement_deg, variant
    )
    assert symfem_name is not None
    if ref == "dual polygon":
        ref += "(4)"
    assert isinstance(deg, int)
    return symfem.create_element(ref, symfem_name, deg, **params)


class CachedSymfemTabulator:
    """Symfem tabulator with caching."""

    def __init__(self, element: FiniteElement):
        """Initialise.

        Args:
            element: Symfem element
        """
        self.element = element
        self.tables: list[tuple[Array, Array]] = []

    def tabulate(self, points: Array) -> Array:
        """Tabulate this element.

        Args:
            points: Points to tabulate at

        Returns:
            Values of basis functions
        """
        import numpy as np

        for i, j in self.tables:
            if i.shape == points.shape and np.allclose(i, points):
                return j
        shape = (points.shape[0], self.element.range_dim, self.element.space_dim)
        table = to_array(self.element.tabulate_basis(points, "xx,yy,zz"))  # type: ignore
        assert not isinstance(table, float)
        table = table.reshape(shape)
        self.tables.append((points, table))
        return table


@pypi_name("symfem")
class SymfemImplementation(Implementation):
    """Symfem implementation."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        out = f'"{string}"'
        for p, v in params.items():
            if p == "variant":
                out += f', {p}="{v}"'
            else:
                raise ValueError(f"Unexpected parameter: {p}")
        return out

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import symfem"

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
        """Generate examples."""
        out = "element = symfem.create_element("
        if reference == "dual polygon":
            out += f'"{reference}(4)",'
        else:
            out += f'"{reference}",'
        out += f' "{name}", {degree}'
        for i, j in params.items():
            if isinstance(j, str):
                out += f', {i}="{j}"'
            else:
                out += f", {i}={j}"
        out += ")"
        return out

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
        """Get verification data."""
        import symfem

        if reference == "dual polygon":
            reference += "(4)"
        e = symfem.create_element(reference, name, degree, **params)  # type: ignore
        edofs = [
            [e.entity_dofs(i, j) for j in range(e.reference.sub_entity_count(i))]
            for i in range(e.reference.tdim + 1)
        ]
        t = CachedSymfemTabulator(e)
        return edofs, lambda points: t.tabulate(points)

    id = "symfem"
    name = "Symfem"
    url = "https://github.com/mscroggs/symfem"
    verification = True
