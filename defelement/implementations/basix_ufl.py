"""Basix.UFL implementation."""

import typing

from defelement.implementations.basix import BasixImplementation
from defelement.implementations.core import Array, Element, Implementation, parse_example


class BasixUFLImplementation(Implementation):
    """Basix.UFL implementation."""

    @staticmethod
    def format(string: typing.Optional[str], params: typing.Dict[str, typing.Any]) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        out = BasixImplementation.format(string, {i: j for i, j in params.items() if i != "shape"})
        if "shape" in params:
            out += f", shape={params['shape']}"
        return out

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import basix\nimport basix.ufl"
        for e in element.examples:
            ref, deg, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0

            try:
                basix_name, input_deg, params = element.get_implementation_string(
                    "basix.ufl", ref, deg, variant)
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {deg} on a {ref}\n"
            out += "element = basix.ufl.element("
            out += f"basix.ElementFamily.{basix_name}, basix.CellType.{ref}, {input_deg}"
            if "lagrange_variant" in params:
                out += f", lagrange_variant=basix.LagrangeVariant.{params['lagrange_variant']}"
            if "dpc_variant" in params:
                out += f", dpc_variant=basix.DPCVariant.{params['dpc_variant']}"
            if "discontinuous" in params:
                assert params["discontinuous"] in ["True", "False"]
                out += f", discontinuous={params['discontinuous']}"
            if "shape" in params:
                if ref == "interval":
                    dim = 1
                elif ref in ["triangle", "quadrilateral"]:
                    dim = 2
                else:
                    dim = 3
                out += ", shape=" + params["shape"].replace("dim", f"{dim}")
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
        import basix
        import basix.ufl

        kwargs: typing.Dict[str, typing.Any]

        ref, deg, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0
        basix_name, input_deg, params = element.get_implementation_string(
            "basix.ufl", ref, deg, variant, any_variant=True)
        kwargs = {}
        if "lagrange_variant" in params:
            kwargs["lagrange_variant"] = getattr(basix.LagrangeVariant, params['lagrange_variant'])
        if "dpc_variant" in params:
            kwargs["dpc_variant"] = getattr(basix.DPCVariant, params['dpc_variant'])
        if "discontinuous" in params:
            kwargs["discontinuous"] = params["discontinuous"] == "True"
        if "shape" in params:
            if ref == "interval":
                dim = 1
            elif ref in ["triangle", "quadrilateral"]:
                dim = 2
            else:
                dim = 3
            kwargs["shape"] = tuple(
                dim if i == "dim" else int(i) for i in params["shape"][1:-1].split(",") if i != "")

        e = basix.ufl.element(
            getattr(basix.ElementFamily, basix_name), getattr(basix.CellType, ref),
            input_deg, **kwargs)
        return e.entity_dofs, lambda points: e.tabulate(0, points)[0].reshape(
            points.shape[0], e.reference_value_size, -1)

    id = "basix.ufl"
    name = "Basix.UFL"
    url = "https://github.com/FEniCS/basix"
    verification = True
    install = "pip3 install git+https://github.com/FEniCS/basix fenics-ufl"
    # install = "pip3 install fenics-basix fenics-ufl"
