"""Implementation in Ferrite.jl."""

import re
import typing

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
    languages = ("julia",)
