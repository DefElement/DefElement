"""FUSE implementation."""

import typing

import sympy
from numpy import float64
from numpy.typing import NDArray

from defelement.element import Element
from defelement.implementations.core import (
    Implementation,
    parse_example,
    pypi_name,
)

# TODO make this a FIAT attribute
true_space_dimension = {
    "Bell": 18,
    "Mardal-Tai-Winther": 9,
    "reduced Hsieh-Clough-Tocher": 9,
    "Arnold-Winther": 24,
    "nonconforming Arnold-Winther": 15,
}


@pypi_name("fuse-element")
class FUSEImplementation(Implementation):
    """FUSE implementation."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        if string.startswith("table:"):
            out = f"fuse.periodic_table({string[6:]}, degree)"
        #started = False
        #for p, v in params.items():
        #    if p == "variant":
        #        if not started:
        #            out += "(..."
        #            started = True
        #        out += f', {p}="{v}"'
        #    elif p in ["subdegree", "reduced"]:
        #        if not started:
        #            out += "(..."
        #            started = True
        #        out += f", {p}={v}"
        #    elif p != "degree":
        #        raise ValueError(f"Unexpected parameter: {p}")
        #if started:
        #    out += ")"
        return out

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
        if name.startswith("table:"):
            name = f"fuse.periodic_table({name[6:]}"
        out = f"element = {name}"
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

        if reference == "interval":
            cell = fuse.line().to_fiat()
        elif reference == "triangle":
            cell = fuse.polygon(3).to_fiat()
        elif reference == "tetrahedron":
            cell = fuse.make_tetrahedron().to_fiat()
        else:
            raise ValueError(f"Unsupported cell: {reference}")
        sd = cell.get_spatial_dimension()
        args = []
        kwargs: dict[str, typing.Any] = {}

        if name.startswith("table:"):
            print(name)
            e = fuse.periodic_table(*[int(n) for n  in name[6:].split(",")], degree).to_fiat()
        else:
            raise NotImplementedError("Cannot verify non periodic table fuse elements")
        print("Created FUSE element in fiat correctly")

        value_size = 1
        for i in e.value_shape():
            value_size *= i
        edofs = [list(i.values()) for i in e.entity_dofs().values()]

        if reference == "triangle":
            edofs[1] = [edofs[1][0], edofs[1][1], edofs[1][2]]
    #    elif reference == "tetrahedron":
    #        edofs[1] = [
    #            edofs[1][5],
    #            edofs[1][4],
    #            edofs[1][3],
    #            edofs[1][2],
    #            edofs[1][1],
    #            edofs[1][0],
    #        ]
    #        edofs[2] = [edofs[2][3], edofs[2][2], edofs[2][1], edofs[2][0]]
    #    elif reference == "quadrilateral":
    #        edofs = [
    #            [edofs[0][0], edofs[0][2], edofs[0][1], edofs[0][3]],
    #            [edofs[1][2], edofs[1][0], edofs[1][1], edofs[1][3]],
    #            [edofs[2][0]],
    #        ]
    #    elif reference == "hexahedron":
    #        edofs = [
    #            [
    #                edofs[0][0],
    #                edofs[0][4],
    #                edofs[0][2],
    #                edofs[0][6],
    #                edofs[0][1],
    #                edofs[0][5],
    #                edofs[0][3],
    #                edofs[0][7],
    #            ],
    #            [
    #                edofs[1][8],
    #                edofs[1][4],
    #                edofs[1][0],
    #                edofs[1][6],
    #                edofs[1][2],
    #                edofs[1][10],
    #                edofs[1][1],
    #                edofs[1][3],
    #                edofs[1][9],
    #                edofs[1][5],
    #                edofs[1][7],
    #                edofs[1][11],
    #            ],
    #            [
    #                edofs[2][4],
    #                edofs[2][2],
    #                edofs[2][0],
    #                edofs[2][1],
    #                edofs[2][3],
    #                edofs[2][5],
    #            ],
    #            [edofs[3][0]],
    #        ]

    #    if element.name in {
    #        "Bernardi-Raugel",
    #        "Guzman-Neilan (first kind)",
    #        "Guzman-Neilan (second kind)",
    #    }:
    #        reduced_dim = e.space_dimension() - (sd + 1) * (sd - 1)
    #    else:
        reduced_dim = true_space_dimension.get(element.name)

        if reduced_dim is not None:
            for dim in range(len(edofs)):
                for i in range(len(edofs[dim])):
                    edofs[dim][i] = [dof for dof in edofs[dim][i] if dof < reduced_dim]

        z = (0,) * sd
        return edofs, lambda points: e.tabulate(0, points)[z][slice(reduced_dim)].T.reshape(
            points.shape[0], value_size, -1
        )

    @classmethod
    def notes(cls, element: Element) -> list[str]:
        """Return a list of notes to include for the implementation of this element."""
        if element.name in true_space_dimension:
            return [
                (
                    "This implementation includes additional DOFs that are used then filtered "
                    "out when mapping the element, as described in Kirby (2018)."
                )
            ]
        return []

    @classmethod
    def references(cls, element: Element) -> list[dict[str, typing.Any]]:
        """Return a list of additional references to include for the implementation of this element."""
        if element.name in true_space_dimension:
            return [
                {
                    "title": "A general approach to transforming finite elements",
                    "author": ["Kirby, Robert C."],
                    "year": 2018,
                    "journal": "SMAI Journal of Computational Mathematics",
                    "volume": 4,
                    "pagestart": 197,
                    "pageend": 224,
                    "doi": "10.5802/smai-jcm.33",
                }
            ]
        return []

    id = "fuse"
    name = "FUSE"
    url = "https://github.com/firedrakeproject/fuse"
    verification = True
    languages = ("python",)
    description = "FUSE is a finite element definition library compatible with the Firedrake ecosystem."
