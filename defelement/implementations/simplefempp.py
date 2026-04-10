"""Simplefem++ implementation."""

import typing
from numpy import float64
from numpy.typing import NDArray

from defelement.element import Element
from defelement.implementations.core import Implementation
from defelement.implementations import jit


class SimplefemppImplementation(Implementation):
    """Simplefem++ implementation."""

    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        return string

    @classmethod
    def example_import(cls, language: str) -> str:
        """Get imports to include at start of example."""
        return "#include <simplefem/lagrange.h>\n\nusing namespace simplefem;"

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
        return f"auto element = {name}({degree});"

    @classmethod
    def install(cls, language: str) -> str | None:
        """Get the command(s) to install this implementation."""
        if language == "cpp":
            return "\n".join(
                [
                    "git clone https://github.com/DefElement/simplefempp",
                    "cd simplefempp",
                    "mkdir build",
                    "cd build",
                    "cmake ..",
                    "sudo make install",
                ]
            )
        return None

    @classmethod
    def version(cls) -> str:
        """Get the version number of this implementation."""
        return "0.9.0"

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
        if degree == 1:
            entity_dofs = [
                [[0], [1], [2]],
                [[], [], []],
                [[]],
            ]
        elif degree == 2:
            entity_dofs = [
                [[0], [2], [5]],
                [[1], [3], [4]],
                [[]],
            ]
        elif degree == 3:
            entity_dofs = [
                [[0], [3], [9]],
                [[1, 2], [4, 7], [6, 8]],
                [[5]],
            ]
        else:
            raise ValueError(f"Unsupported degree: {degree}")

        tabulate = jit.cpp(
            inputs=[jit.ndarray("pts", 2), jit.integer("degree")],
            function=(
                f"auto element = {name}(degree);\n"
                "INIT values;\n"
                "std::vector<double> point(2);\n"
                "for (std::size_t i = 0; i < pts.extent(0); ++i)\n"
                "  for (std::size_t j = 0; j < element.dim(); ++j) {\n"
                "    point[0] = pts(i, 0);\n"
                "    point[1] = pts(i, 1);\n"
                "    values(i, 0, j) = element.evaluate(j, point);\n"
                "  }"
            ),
            outputs=[jit.ndarray("values", 3, shape=("pts.extent(0)", 1, "element.dim()"))],
            imports=cls.example_import("cpp") + "\n#include <vector>",
            id=f"{cls.name}-{cls.version}-{name}-{reference}",
            packages=[("SimpleFem", "simplefem")],
        )
        return entity_dofs, lambda pts: tabulate(pts, degree)  # type: ignore

    id = "simplefempp"
    name = "simplefem++"
    url = "https://github.com/DefElement/simplefempp"
    languages = ["cpp"]
    verification = True
