"""FIAT implementation."""

import typing

import sympy

from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
    parse_example,
)

# TODO make this a FIAT attribute
true_space_dimension = {
    "Bell": 18,
    "Mardal-Tai-Winther": 9,
    "reduced Hsieh-Clough-Tocher": 9,
    "Arnold-Winther": 24,
    "nonconforming Arnold-Winther": 15,
}


class FIATImplementation(Implementation):
    """FIAT implementation."""

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
        out = f"FIAT.{string}"
        started = False
        for p, v in params.items():
            if p == "variant":
                if not started:
                    out += "(..."
                    started = True
                out += f', {p}="{v}"'
            elif p in ["subdegree", "reduced"]:
                if not started:
                    out += "(..."
                    started = True
                out += f", {p}={v}"
            elif p != "degree":
                raise ValueError(f"Unexpected parameter: {p}")
        if started:
            out += ")"
        return out

    @classmethod
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import FIAT"

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
        if reference in ["interval", "triangle", "tetrahedron"]:
            cell = f'FIAT.ufc_cell("{reference}")'
        elif reference == "quadrilateral":
            cell = "FIAT.reference_element.UFCQuadrilateral()"
        elif reference == "hexahedron":
            cell = "FIAT.reference_element.UFCHexahedron()"
        else:
            raise ValueError(f"Unsupported cell: {reference}")
        out = f"element = FIAT.{name}({cell}"
        if params.get("degree", "") != "None":
            out += f", {degree}"
        for i, j in params.items():
            if i == "variant":
                out += f', {i}="{j}"'
            if i == "subdegree":
                subdegree = parse_example(example)[1]
                out += f", {i}={sympy.S(j).subs(sympy.Symbol('k'), subdegree)}"
            if i == "reduced":
                out += f", {i}={j}"
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
        import FIAT

        if reference in ["interval", "triangle", "tetrahedron"]:
            cell = FIAT.ufc_cell(reference)
        elif reference == "quadrilateral":
            cell = FIAT.reference_element.UFCQuadrilateral()
        elif reference == "hexahedron":
            cell = FIAT.reference_element.UFCHexahedron()
        else:
            raise ValueError(f"Unsupported cell: {reference}")

        args = []
        kwargs: dict[str, typing.Any] = {}

        if params.get("degree", "") != "None":
            args.append(degree)

        if "variant" in params:
            kwargs["variant"] = params["variant"]

        if "reduced" in params:
            kwargs["reduced"] = bool(params["reduced"])

        e = getattr(FIAT, name)(cell, *args, **kwargs)

        value_size = 1
        for i in e.value_shape():
            value_size *= i
        edofs = [list(i.values()) for i in e.entity_dofs().values()]
        if reference == "quadrilateral":
            edofs = [
                [edofs[0][0], edofs[0][2], edofs[0][1], edofs[0][3]],
                [edofs[1][2], edofs[1][0], edofs[1][1], edofs[1][3]],
                [edofs[2][0]],
            ]
        if reference == "hexahedron":
            edofs = [
                [
                    edofs[0][0],
                    edofs[0][4],
                    edofs[0][2],
                    edofs[0][6],
                    edofs[0][1],
                    edofs[0][5],
                    edofs[0][3],
                    edofs[0][7],
                ],
                [
                    edofs[1][8],
                    edofs[1][4],
                    edofs[1][0],
                    edofs[1][6],
                    edofs[1][2],
                    edofs[1][10],
                    edofs[1][1],
                    edofs[1][3],
                    edofs[1][9],
                    edofs[1][5],
                    edofs[1][7],
                    edofs[1][11],
                ],
                [
                    edofs[2][4],
                    edofs[2][2],
                    edofs[2][0],
                    edofs[2][1],
                    edofs[2][3],
                    edofs[2][5],
                ],
                [edofs[3][0]],
            ]

        sd = cell.get_spatial_dimension()
        if element.name in {
            "Bernardi-Raugel",
            "Guzman-Neilan (first kind)",
            "Guzman-Neilan (second kind)",
        }:
            reduced_dim = e.space_dimension() - (sd + 1) * (sd - 1)
        else:
            reduced_dim = true_space_dimension.get(element.name)

        if reduced_dim is not None:
            for dim in range(len(edofs)):
                for i in range(len(edofs[dim])):
                    edofs[dim][i] = [dof for dof in edofs[dim][i] if dof < reduced_dim]

        z = (0,) * sd
        return edofs, lambda points: e.tabulate(0, points)[z][
            slice(reduced_dim)
        ].T.reshape(points.shape[0], value_size, -1)

    @classmethod
    def notes(cls, element: Element) -> typing.List[str]:
        """Return a list of notes to include for the implementation of this element.

        Args:
            element: Element data

        Returns:
            List of notes
        """
        if element.name in true_space_dimension:
            return [
                "This implementation includes additional DOFs that are used then filtered "
                "out when mapping the element, as described in Kirby (2018)."
            ]
        return []

    @classmethod
    def references(cls, element: Element) -> typing.List[typing.Dict[str, typing.Any]]:
        """Return a list of additional references to include for the implementation of this element.

        Args:
            element: Element data

        Returns:
            List of references
        """
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

    id = "fiat"
    name = "FIAT"
    url = "https://github.com/firedrakeproject/fiat"
    verification = True
    install = "pip3 install git+https://github.com/firedrakeproject/fiat.git"
