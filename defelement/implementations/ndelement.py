"""NDElement implementation."""

import typing

from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
)


class NDElementImplementation(Implementation):
    """NDElement implementation."""

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
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[int]]], typing.Callable[[Array], Array]
    ]:
        """Get verification data.

        Args:
            name: The name of this element for this implementation
            reference: The name of the reference cell
            degree: The degree of this example
            params: Additional parameters set in the .def file
            element: Element data
            example: Example data

        Returns:
            List of entity dofs, and tabulation function
        """
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

        return entity_dofs, lambda points: e.tabulate(points, 0)[:, :, :, 0].transpose(
            (2, 0, 1)
        )

    id = "ndelement"
    name = "NDElement"
    url = "https://github.com/bempp/nd"
    verification = True
    install = "pip3 install ndelement"
