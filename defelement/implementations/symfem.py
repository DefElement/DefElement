"""Symfem implementation."""

import typing

from symfem.finite_element import FiniteElement

from defelement.implementations.core import Array, Element, Implementation, parse_example
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

    ref, deg, variant, kwargs = parse_example(example)
    symfem_name, input_deg, params = element.get_implementation_string("symfem", ref, deg, variant)
    assert symfem_name is not None
    if ref == "dual polygon":
        ref += "(4)"
    assert isinstance(input_deg, int)
    return symfem.create_element(ref, symfem_name, input_deg, **params)


class CachedSymfemTabulator:
    """Symfem tabulator with caching."""

    def __init__(self, element: FiniteElement):
        """Initialise.

        Args:
            element: Symfem element
        """
        self.element = element
        self.tables: typing.List[typing.Tuple[Array, Array]] = []

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


class SymfemImplementation(Implementation):
    """Symfem implementation."""

    @staticmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        out = f"\"{string}\""
        for p, v in params.items():
            if p == "variant":
                out += f", {p}=\"{v}\""
        return out

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import symfem"
        for e in element.examples:
            ref, deg, variant, kwargs = parse_example(e)
            symfem_name, input_deg, params = element.get_implementation_string(
                "symfem", ref, deg, variant)

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {deg} on a {ref}\n"
            if ref == "dual polygon":
                out += f"element = symfem.create_element(\"{ref}(4)\","
            else:
                out += f"element = symfem.create_element(\"{ref}\","
            if "variant" in params:
                out += f" \"{symfem_name}\", {input_deg}, variant=\"{params['variant']}\""
            else:
                out += f" \"{symfem_name}\", {input_deg}"
            for i, j in kwargs.items():
                if isinstance(j, str):
                    out += f", {i}=\"{j}\""
                else:
                    out += f", {i}={j}"
            out += ")"
        return out

    @staticmethod
    def verify(
        element: Element, example: str
    ) -> typing.Tuple[typing.List[typing.List[typing.List[int]]], typing.Callable[[Array], Array]]:
        """Get verification data.

        Args:
            element: Element data
            example: Example data

        Returns:
            List of entity dofs, and tabulation function
        """
        import symfem

        ref, deg, variant, kwargs = parse_example(example)
        symfem_name, input_deg, params = element.get_implementation_string(
            "symfem", ref, deg, variant)
        if ref == "dual polygon":
            ref += "(4)"
        assert isinstance(input_deg, int)
        e = symfem.create_element(ref, symfem_name, input_deg, **params)
        edofs = [[e.entity_dofs(i, j) for j in range(e.reference.sub_entity_count(i))]
                 for i in range(e.reference.tdim + 1)]
        t = CachedSymfemTabulator(e)
        return edofs, lambda points: t.tabulate(points)

    id = "symfem"
    name = "Symfem"
    url = "https://github.com/mscroggs/symfem"
    install = "pip3 install symfem"
    verification = True
