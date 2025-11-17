"""Basix.UFL implementation."""

import typing

from defelement.implementations.basix import BasixImplementation
from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
    parse_example,
)


class BasixUFLImplementation(Implementation):
    """Basix.UFL implementation."""

    @staticmethod
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
        out = BasixImplementation.format(
            string, {i: j for i, j in params.items() if i != "shape"}
        )
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
                    "basix.ufl", ref, deg, variant
                )
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {deg} on a {ref}\n"
            out += "element = basix.ufl.element("
            out += (
                f"basix.ElementFamily.{basix_name}, basix.CellType.{ref}, {input_deg}"
            )
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
        import basix
        import basix.ufl

        kwargs: typing.Dict[str, typing.Any]

        ref, deg, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0
        basix_name, input_deg, params = element.get_implementation_string(
            "basix.ufl", ref, deg, variant, any_variant=True
        )
        kwargs = {}
        if "lagrange_variant" in params:
            kwargs["lagrange_variant"] = getattr(
                basix.LagrangeVariant, params["lagrange_variant"]
            )
        if "dpc_variant" in params:
            kwargs["dpc_variant"] = getattr(basix.DPCVariant, params["dpc_variant"])
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
                dim if i == "dim" else int(i)
                for i in params["shape"][1:-1].split(",")
                if i != ""
            )

        e = basix.ufl.element(
            getattr(basix.ElementFamily, basix_name),
            getattr(basix.CellType, ref),
            input_deg,
            **kwargs,
        )
        return e.entity_dofs, lambda points: e.tabulate(0, points)[0].reshape(
            points.shape[0], e.reference_value_size, -1
        )

    id = "basix.ufl"
    name = "Basix.UFL"
    url = "https://github.com/FEniCS/basix"
    verification = True
    install = "pip3 install git+https://github.com/FEniCS/basix fenics-ufl"


class CustomBasixUFLImplementation(BasixUFLImplementation):
    """Basix.UFL implementation via custom element."""

    @staticmethod
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
        raise NotImplementedError()

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        import symfem
        import symfem.basix_interface

        out = "import basix\nimport basix.ufl\nimport numpy as np"

        for e in element.examples:
            cell, degree, variant, kwargs = parse_example(e)
            symfem_name, symfem_degree, params = element.get_implementation_string(
                "symfem", cell, degree, variant
            )
            if "variant" in params:
                kwargs["variant"] = params["variant"]
            symfem_e = symfem.create_element(cell, symfem_name, symfem_degree, **kwargs)  # type: ignore

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {degree} on a {cell}\n"

            out += symfem.basix_interface.generate_basix_element_code(
                symfem_e, include_comment=False, include_imports=False, ufl=True
            )

        return out

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
        import symfem
        import symfem.basix_interface

        cell, degree, variant, kwargs = parse_example(example)
        symfem_name, symfem_degree, params = element.get_implementation_string(
            "symfem", cell, degree, variant
        )
        if "variant" in params:
            kwargs["variant"] = params["variant"]
        symfem_e = symfem.create_element(cell, symfem_name, symfem_degree, **kwargs)  # type: ignore

        e = symfem.basix_interface.create_basix_element(symfem_e, ufl=True)

        return e.entity_dofs, lambda points: e.tabulate(0, points)[0].reshape(
            points.shape[0], e.reference_value_size, -1
        )

    @staticmethod
    def implemented(element: Element) -> bool:
        """Check if an element is implemented.

        This can be used to overrule Element's implemented function.

        Args:
            element: The element

        Returns:
            Example code
        """
        import symfem
        import symfem.basix_interface

        for e in element.examples:
            cell, degree, variant, kwargs = parse_example(e)
            symfem_name, symfem_degree, params = element.get_implementation_string(
                "symfem", cell, degree, variant
            )
            if "variant" in params:
                kwargs["variant"] = params["variant"]
            symfem_e = symfem.create_element(cell, symfem_name, symfem_degree, **kwargs)  # type: ignore
            try:
                symfem.basix_interface.generate_basix_element_code(symfem_e)
            except NotImplementedError:
                return False
        return True

    id = "*(symfem -> basix.ufl)"
