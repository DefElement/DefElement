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

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        out = BasixImplementation.format(
            string, {i: j for i, j in params.items() if i != "shape"}
        )
        if "shape" in params:
            out += f", shape={params['shape']}"
        return out

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import basix\nimport basix.ufl"

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
        out = "element = basix.ufl.element("
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
        if "shape" in params:
            if reference == "interval":
                dim = 1
            elif reference in ["triangle", "quadrilateral"]:
                dim = 2
            else:
                dim = 3
            out += ", shape=" + params["shape"].replace("dim", f"{dim}")
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
        import basix
        import basix.ufl

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
            if reference == "interval":
                dim = 1
            elif reference in ["triangle", "quadrilateral"]:
                dim = 2
            else:
                dim = 3
            kwargs["shape"] = tuple(
                dim if i == "dim" else int(i)
                for i in params["shape"][1:-1].split(",")
                if i != ""
            )

        e = basix.ufl.element(
            getattr(basix.ElementFamily, name),
            getattr(basix.CellType, reference),
            degree,
            **kwargs,
        )

        entity_dofs = e.entity_dofs
        if reference == "triangle":
            entity_dofs[1] = [entity_dofs[1][2], entity_dofs[1][1], entity_dofs[1][0]]
        elif reference == "tetrahedron":
            entity_dofs[1] = [entity_dofs[1][5], entity_dofs[1][4], entity_dofs[1][3], entity_dofs[1][2], entity_dofs[1][1], entity_dofs[1][0]]
            entity_dofs[2] = [entity_dofs[2][3], entity_dofs[2][2], entity_dofs[2][1], entity_dofs[2][0]]

        return entity_dofs, lambda points: e.tabulate(0, points)[0].reshape(
            points.shape[0], e.reference_value_size, -1
        )

    id = "basix.ufl"
    name = "Basix.UFL"
    url = "https://github.com/FEniCS/basix"
    verification = True
    install = "pip3 install git+https://github.com/FEniCS/basix fenics-ufl"


class CustomBasixUFLImplementation(BasixUFLImplementation):
    """Basix.UFL implementation via custom element."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        raise NotImplementedError()

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import basix\nimport basix.ufl\nimport numpy as np"

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
        import symfem
        import symfem.basix_interface

        cell, degree, variant, kwargs = parse_example(example)
        symfem_name, symfem_degree, params = element.get_implementation_string(
            "symfem", cell, degree, variant
        )
        if "variant" in params:
            kwargs["variant"] = params["variant"]
        symfem_e = symfem.create_element(cell, symfem_name, symfem_degree, **kwargs)  # type: ignore

        return symfem.basix_interface.generate_basix_element_code(
            symfem_e, include_comment=False, include_imports=False, ufl=True
        )

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
        import symfem.basix_interface

        kwargs = {}
        if "variant" in params:
            kwargs["variant"] = params["variant"]
        symfem_e = symfem.create_element(reference, name, degree, **kwargs)  # type: ignore

        e = symfem.basix_interface.create_basix_element(symfem_e, ufl=True)

        entity_dofs = e.entity_dofs
        if reference == "triangle":
            entity_dofs[1] = [entity_dofs[1][2], entity_dofs[1][1], entity_dofs[1][0]]
        elif reference == "tetrahedron":
            entity_dofs[1] = [entity_dofs[1][5], entity_dofs[1][4], entity_dofs[1][3], entity_dofs[1][2], entity_dofs[1][1], entity_dofs[1][0]]
            entity_dofs[2] = [entity_dofs[2][3], entity_dofs[2][2], entity_dofs[2][1], entity_dofs[2][0]]

        return entity_dofs, lambda points: e.tabulate(0, points)[0].reshape(
            points.shape[0], e.reference_value_size, -1
        )

    @classmethod
    def implemented(cls, element: Element) -> bool:
        """Check if an element is implemented."""
        # Elements with DOFs that include derivatives
        if element.filename in [
            "alfeld-sorokina",
            "argyris",
            "arnold-boffi-falk",
            "bell",
            "bernardi-raugel",
            "bogner-fox-schmitt",
            "hermite",
            "morley",
            "morley-wang-xu",
            "taylor",
            "wu-xu",
        ]:
            return False

        # D(div curl) elements
        if element.filename in [
            "gopalakrishnan-lederer-schoberl",
        ]:
            return False

        # Macro elements
        if element.filename in [
            "alfeld-sorokina",
            "guzman-neilan",
            "guzman-neilan2",
            "hsieh-clough-tocher",
            "johnson-mercier",
            "p1-iso-p2",
            "p1-macro",
            "reduced-hsieh-clough-tocher",
        ]:
            return False

        # Elements with different numbers of DOFs on entities of the same type
        if element.filename in [
            "fortin-soulie",
            "transition",
        ]:
            return False

        # Mixed elements
        if element.filename in [
            "mini",
            "pechstein-schoberl",
            "taylor-hood",
            "scott-vogelius",
        ]:
            return False

        # Dual elements
        if element.filename in [
            "buffa-christiansen",
            "dual",
            "rotated-buffa-christiansen",
        ]:
            return False

        # non-Ciarlet elements
        if element.filename in [
            "direct-serendipity",
            "enriched-galerkin",
            "lfeg",
            "rotated-buffa-christiansen",
        ]:
            return False

        return True

    id = "*(symfem -> basix.ufl)"
