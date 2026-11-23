"""FUSE implementation."""

import typing

from numpy import float64
from numpy.typing import NDArray

from defelement.element import Element
from defelement.implementations.core import Implementation, pypi_name


@pypi_name("fuse-element")
class FUSEImplementation(Implementation):
    """FUSE implementation."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        if string.startswith("table:"):
            return f"fuse.periodic_table({string[6:]}, degree)"
        raise ValueError(f"Unsupported FUSE implementation string: {string}")

    @classmethod
    def example_import(cls, language: str) -> str:
        """Get imports to include at start of example."""
        return "import fuse"

    @classmethod
    def single_example(
        cls,
        name: str,
        reference: str,
        degree: int,
        params: dict[str, str],
        language: str,
        element: Element,
        example: str,
    ) -> str:
        """Generate code for a single example."""
        if not name.startswith("table:"):
            raise ValueError(f"Unsupported FUSE implementation string: {name}")
        out = f"element = fuse.periodic_table({name[6:]}"
        if params.get("degree", "") != "None":
            out += f", {degree}"
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
    ) -> tuple[list[list[list[int]]], typing.Callable[[NDArray[float64]], NDArray[float64]]]:
        """Get verification data."""
        import fuse
        import numpy as np
        import symfem

        if reference not in ["interval", "triangle", "tetrahedron"]:
            raise NotImplementedError(f"FUSE verification not implemented on {reference}")
        if not name.startswith("table:"):
            raise NotImplementedError("Cannot verify non periodic table FUSE elements")

        e = fuse.periodic_table(*[int(n) for n in name[6:].split(",")], degree).to_fiat()
        if e.value_shape() != ():
            raise NotImplementedError("FUSE verification of vector-valued elements")

        # FUSE cells are not DefElement's reference cells (e.g. the FUSE triangle is
        # equilateral and centred on the origin), so map DefElement's reference cell
        # affinely onto the FUSE cell, sending DefElement vertex i to FUSE vertex i.
        cell = e.get_reference_element()
        r = symfem.create_reference(reference)
        fuse_verts = np.array(cell.get_vertices(), dtype=float64)
        def_verts = np.array([[float(c) for c in v] for v in r.vertices])
        jacobian = (fuse_verts[1:] - fuse_verts[0]).T @ np.linalg.inv(
            (def_verts[1:] - def_verts[0]).T
        )

        # Reorder the entity DOFs into DefElement's sub-entity numbering by matching
        # each sub-entity's set of vertices.
        topology = cell.get_topology()
        fuse_edofs = e.entity_dofs()
        edofs: list[list[list[int]]] = []
        for dim in range(r.tdim + 1):
            lookup = {frozenset(vs): n for n, vs in topology[dim].items()}
            edofs.append(
                [list(fuse_edofs[dim][lookup[frozenset(se)]]) for se in r.sub_entities(dim)]
            )

        z = (0,) * r.tdim

        def tabulate(points: NDArray[float64]) -> NDArray[float64]:
            mapped = fuse_verts[0] + (points - def_verts[0]) @ jacobian.T
            return e.tabulate(0, mapped)[z].T.reshape(points.shape[0], 1, -1)

        return edofs, tabulate

    id = "fuse"
    name = "FUSE"
    url = "https://github.com/firedrakeproject/fuse"
    verification = True
    languages = ("python",)
    description = "FUSE is a finite element definition library compatible with the Firedrake ecosystem."
