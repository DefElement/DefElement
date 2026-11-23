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

        triple = fuse.periodic_table(*[int(n) for n in name[6:].split(",")], degree)
        e = triple.to_fiat()
        pullback = triple.pullback()
        if pullback not in ["identity", "covariant Piola", "contravariant Piola"]:
            raise NotImplementedError(f"FUSE verification with {pullback} pullback is not implemented")

        # FUSE default cells differ from DefElement's reference cells so map DefElement's
        # reference cell affinely onto the FUSE cell, sending DefElement vertex i to FUSE vertex i.
        cell = e.get_reference_element()
        r = symfem.create_reference(reference)
        fuse_verts = np.array(cell.get_vertices(), dtype=float64)
        def_verts = np.array([[float(c) for c in v] for v in r.vertices])
        jacobian = (fuse_verts[1:] - fuse_verts[0]).T @ np.linalg.inv((def_verts[1:] - def_verts[0]).T)

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

        # Pull the values on the FUSE cell back to DefElement's reference cell.
        if pullback == "covariant Piola":
            value_map = jacobian.T
        elif pullback == "contravariant Piola":
            value_map = np.linalg.det(jacobian) * np.linalg.inv(jacobian)
        else:
            value_map = None

        value_size = 1
        for i in e.value_shape():
            value_size *= i
        z = (0,) * r.tdim

        def tabulate(points: NDArray[float64]) -> NDArray[float64]:
            mapped = fuse_verts[0] + (points - def_verts[0]) @ jacobian.T
            table = e.tabulate(0, mapped)[z].T.reshape(points.shape[0], value_size, -1)
            if value_map is not None:
                table = np.einsum("ij,pjd->pid", value_map, table)
            return table

        return edofs, tabulate

    id = "fuse"
    name = "FUSE"
    url = "https://github.com/firedrakeproject/fuse"
    verification = True
    languages = ("python",)
    description = "FUSE is a finite element definition library compatible with the Firedrake ecosystem."
