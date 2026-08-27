"""Implementation in Ferrite.jl."""

import re
import typing

from numpy import float64
from numpy.typing import NDArray

from defelement.element import Element
from defelement.implementations.core import Implementation, NotImplementedOnReference

# DefElement reference cell names mapped to the Ferrite.jl reference shapes
reference_shapes = {
    "interval": "RefLine",
    "triangle": "RefTriangle",
    "quadrilateral": "RefQuadrilateral",
    "tetrahedron": "RefTetrahedron",
    "hexahedron": "RefHexahedron",
    "prism": "RefPrism",
    "pyramid": "RefPyramid",
}

# The registry file that Julia's package manager resolves Ferrite's versions from
versions_url = (
    "https://raw.githubusercontent.com/JuliaRegistries/General/master/F/Ferrite/Versions.toml"
)


class FerriteImplementation(Implementation):
    """Implementation in Ferrite.jl."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        out = string
        for p, v in params.items():
            if p == "vdim":
                out += f"^{v}"
            else:
                raise ValueError(f"Unexpected parameter: {p}")
        return out

    @classmethod
    def example_import(cls, language: str) -> str:
        """Get imports to include at start of example."""
        if language != "julia":
            raise ValueError(f"Unsupported language: {language}")
        return "using Ferrite"

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
        if language != "julia":
            raise ValueError(f"Unsupported language: {language}")
        if reference not in reference_shapes:
            raise NotImplementedOnReference()
        out = f"ip = {name}{{{reference_shapes[reference]}, {degree}}}()"
        for p, v in params.items():
            if p == "vdim":
                out += f"^{v}"
            else:
                raise ValueError(f"Unexpected parameter: {p}")
        return out

    @classmethod
    def install(cls, language: str) -> str | None:
        """Get the command(s) to install this implementation."""
        if language == "julia":
            return "julia -e 'using Pkg; Pkg.add(\"Ferrite\")'"
        return None

    @classmethod
    def version(cls) -> str:
        """Get the version number of this implementation."""
        import requests

        # Ferrite is not registered on PyPI, so the latest release is read from the entries of
        # Julia's General registry, which are of the form `["1.2.3"]`
        versions = re.findall(
            r'^\["([0-9]+(?:\.[0-9]+)*)"\]', requests.get(versions_url).text, re.MULTILINE
        )
        return max(versions, key=lambda v: tuple(int(i) for i in v.split(".")))

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
        import numpy as np
        import symfem
        from juliacall import Main as jl

        jl.seval("using Ferrite")

        shape = reference_shapes[reference]
        vdim = None
        for p, v in params.items():
            if p == "vdim":
                vdim = int(v)
            else:
                raise ValueError(f"Unexpected parameter: {p}")
        # Entity DOFs must be queried from the scalar interpolation: DOF d of the scalar
        # interpolation corresponds to DOFs vdim*d, ..., vdim*d + vdim - 1 of the vectorized one
        scalar_ip = jl.seval(f"{name}{{{shape}, {degree}}}()")
        ip = jl.seval(f"{name}{{{shape}, {degree}}}()^{vdim}") if vdim is not None else scalar_ip

        # Ferrite defines hypercube cells on [-1, 1]^d while DefElement uses [0, 1]^d; the
        # other cells are identical up to vertex numbering. As the map between the cells is
        # a uniform scaling, mapped basis functions differ from DefElement's by at most a
        # constant scalar factor, so the tabulated values can be compared without applying
        # the (Piola) mapping of the element.
        hypercube = reference in ("interval", "quadrilateral", "hexahedron")

        # perm[i] is the DefElement number of Ferrite's vertex i
        r = symfem.create_reference(reference)
        def_verts = np.array([[float(c) for c in v] for v in r.vertices])
        fer_verts = np.array(
            [tuple(v) for v in jl.seval(f"Ferrite.reference_coordinates(Lagrange{{{shape}, 1}}())")]
        )
        if hypercube:
            fer_verts = (fer_verts + 1) / 2
        perm = [
            next(j for j, dv in enumerate(def_verts) if np.allclose(fv, dv)) for fv in fer_verts
        ]

        entity_dofs: list[list[list[int]]] = [
            [[] for _ in range(r.sub_entity_count(d))] for d in range(r.tdim + 1)
        ]
        for v_n, dofs in enumerate(jl.Ferrite.vertexdof_indices(scalar_ip)):
            entity_dofs[0][perm[v_n]] = [int(d) - 1 for d in dofs]
        for dim, fer_dofs in [
            (1, jl.Ferrite.edgedof_interior_indices(scalar_ip)),
            (2, jl.Ferrite.facedof_interior_indices(scalar_ip)),
        ]:
            if dim >= r.tdim:
                break
            fer_ents = jl.seval(
                f"Ferrite.reference_edges({shape})"
                if dim == 1
                else f"Ferrite.reference_faces({shape})"
            )
            def_ents = [frozenset(e) for e in (r.edges if dim == 1 else r.faces)]
            for e_n, e_verts in enumerate(fer_ents):
                e_set = frozenset(perm[int(v) - 1] for v in e_verts)
                entity_dofs[dim][def_ents.index(e_set)] = [int(d) - 1 for d in fer_dofs[e_n]]
        # The remaining DOFs belong to the interior of the cell. This is computed as the
        # complement of the lower-dimensional entity DOFs rather than queried from Ferrite
        # since Ferrite associates the DOFs of discontinuous interpolations with no entity.
        assigned = {d for dofs in entity_dofs for e_dofs in dofs for d in e_dofs}
        nbasis = int(jl.Ferrite.getnbasefunctions(scalar_ip))
        entity_dofs[r.tdim][0] = [d for d in range(nbasis) if d not in assigned]
        if vdim is not None:
            entity_dofs = [
                [[vdim * d + c for d in e_dofs for c in range(vdim)] for e_dofs in dofs]
                for dofs in entity_dofs
            ]

        tabulate_jl = jl.seval("""
        (ip, pts) -> begin
            npts, dim = size(pts)
            nbasis = Ferrite.getnbasefunctions(ip)
            ncomp = length(Ferrite.reference_shape_value(ip, Vec{dim}(i -> 0.0), 1))
            table = zeros(npts, ncomp, nbasis)
            for p in 1:npts
                x = Vec{dim}(i -> pts[p, i])
                for b in 1:nbasis
                    for (c, v) in enumerate(Ferrite.reference_shape_value(ip, x, b))
                        table[p, c, b] = v
                    end
                end
            end
            table
        end
        """)

        def tabulate(points: NDArray[float64]) -> NDArray[float64]:
            if hypercube:
                points = 2 * points - 1
            return np.asarray(tabulate_jl(ip, points))

        return entity_dofs, tabulate

    @classmethod
    def notes(cls, element: Element) -> list[str]:
        """Return a list of notes to include for the implementation of this element."""
        if element.filename == "serendipity":
            return [
                (
                    "Ferrite.jl uses point evaluations at the midpoints of the edges of the cell "
                    "in place of the integral moments used in DefElement's definition of this "
                    "element. Its basis functions therefore differ from the ones shown here, "
                    "although they span the same space."
                )
            ]
        return []

    id = "ferrite"
    name = "Ferrite.jl"
    url = "https://github.com/Ferrite-FEM/Ferrite.jl"
    verification = True
    languages = ("julia",)
