"""NDElement implementation."""

import typing
from numpy import float64
from numpy.typing import NDArray

from defelement.implementations.core import Implementation, Element
# <pypi_name>
from defelement.implementations.core import pypi_name


@pypi_name("ndelement")
class NDElementImplementation(Implementation):
    """NDElement implementation."""
    # </pypi_name>

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        out = f"Family.{string}"
        for p, v in params.items():
            out += f", {p}="
            if p == "continuity":
                out += f"Continuity.{v}"
            else:
                raise ValueError(f"Unexpected parameter: {p}")
        return out

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "from ndelement import ciarlet\nfrom ndelement.reference_cell import ReferenceCellType"

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
        out = "family = ciarlet.create_family("
        out += f"ciarlet.Family.{name}, {degree}"
        if "continuity" in params:
            assert params["continuity"] in ["Standard", "Discontinuous"]
            out += f", continuity=ciarlet.Continuity.{params['continuity']}"
        out += ")\n"
        out += f"element = family.element(ReferenceCellType.{reference[0].upper() + reference[1:]})"
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
    ) -> tuple[
        list[list[list[int]]], typing.Callable[[NDArray[float64]], NDArray[float64]]
    ]:
        """Get verification data."""
        from ndelement.ciarlet import Continuity, Family, create_family
        from ndelement.reference_cell import ReferenceCellType, entity_counts

        kwargs = {}
        if "continuity" in params:
            kwargs["continuity"] = getattr(Continuity, params["continuity"])

        cell = getattr(ReferenceCellType, reference[0].upper() + reference[1:])
        e = create_family(getattr(Family, name), degree, **kwargs).element(cell)
        entity_dofs = [
            [e.entity_dofs(dim, entity) for entity in range(n)]
            for dim, n in enumerate(entity_counts(cell))
            if n > 0
        ]

        if reference == "triangle":
            entity_dofs[1] = [entity_dofs[1][2], entity_dofs[1][1], entity_dofs[1][0]]
        elif reference == "tetrahedron":
            entity_dofs[1] = [
                entity_dofs[1][5],
                entity_dofs[1][4],
                entity_dofs[1][3],
                entity_dofs[1][2],
                entity_dofs[1][1],
                entity_dofs[1][0],
            ]
            entity_dofs[2] = [
                entity_dofs[2][3],
                entity_dofs[2][2],
                entity_dofs[2][1],
                entity_dofs[2][0],
            ]

        return entity_dofs, lambda points: e.tabulate(points, 0)[:, :, :, 0].transpose(
            (2, 0, 1)
        )

    id = "ndelement"
    name = "NDElement"
    url = "https://github.com/bempp/nd"
    verification = True
