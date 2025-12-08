"""Basix implementation."""

import typing

from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
)


class BasixImplementation(Implementation):
    """Basix implementation."""

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
        out = f"basix.ElementFamily.{string}"
        for p, v in params.items():
            out += f", {p}="
            if p == "lagrange_variant":
                out += f"basix.LagrangeVariant.{v}"
            elif p == "dpc_variant":
                out += f"basix.DPCVariant.{v}"
            elif p == "discontinuous":
                out += v
            else:
                raise ValueError(f"Unexpected parameter: {p}")
        return out

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import basix"

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
        """Generate examples.

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
        out = "element = basix.create_element("
        out += f"basix.ElementFamily.{name}, basix.CellType.{reference}, {degree}"
        if "lagrange_variant" in params:
            out += (
                f", lagrange_variant=basix.LagrangeVariant.{params['lagrange_variant']}"
            )
        if "dpc_variant" in params:
            out += f", dpc_variant=basix.DPCVariant.{params['dpc_variant']}"
        if "discontinuous" in params:
            assert params["discontinuous"] in ["True", "False"]
            out += f", discontinuous={params['discontinuous']}"
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
        import basix

        kwargs = {}
        if "lagrange_variant" in params:
            kwargs["lagrange_variant"] = getattr(
                basix.LagrangeVariant, params["lagrange_variant"]
            )
        if "dpc_variant" in params:
            kwargs["dpc_variant"] = getattr(basix.DPCVariant, params["dpc_variant"])
        if "discontinuous" in params:
            kwargs["discontinuous"] = params["discontinuous"] == "True"

        e = basix.create_element(
            getattr(basix.ElementFamily, name),
            getattr(basix.CellType, reference),
            degree,
            **kwargs,
        )
        return e.entity_dofs, lambda points: e.tabulate(0, points)[0].transpose(
            (0, 2, 1)
        )

    id = "basix"
    name = "Basix"
    url = "https://github.com/FEniCS/basix"
    verification = True
    install = "pip3 install fenics-basix"
