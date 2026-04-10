"""Simplefem implementation."""

# <intro>
import typing
from numpy import float64
from numpy.typing import NDArray

from defelement.element import Element
from defelement.implementations import jit
from defelement.implementations.core import Implementation


class SimplefemImplementation(Implementation):
    """Simplefem implementation."""

    # </intro>

    # <format>
    @classmethod
    def format(cls, string: str, params: dict[str, typing.Any]) -> str:
        """Format implementation string."""
        return string

    # </format>

    # <example>
    @classmethod
    def example_import(cls, language: str) -> str:
        """Get imports to include at start of example."""
        return "import simplefem"

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
        return f"element = simplefem.{name}({degree})"

    # </example>

    # <install>
    @classmethod
    def install(cls, language: str) -> str | None:
        """Get the command(s) to install this implementation."""
        if language == "python":
            return "pip3 install git+https://github.com/DefElement/simplefem"
        return None

    # </install>

    # <version>
    @classmethod
    def version(cls) -> str:
        """Get the version number of this implementation."""
        import simplefem

        return simplefem.__version__

    # </version>

    # <verify1>
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
        # </verify1>
        # <verify2>
        import simplefem
        import numpy as np
        # </verify2>

        # <verify3>
        e = getattr(simplefem, name)(degree)
        # </verify3>

        # <verify4>
        entity_dofs: list[list[list[int]]] = [[[], [], []], [[], [], []], [[]]]

        for i, p in enumerate(e.evaluation_points):
            # DOFs associated with vertices
            if np.allclose(p, [-1, 0]):
                entity_dofs[0][0].append(i)
            elif np.allclose(p, [1, 0]):
                entity_dofs[0][1].append(i)
            elif np.allclose(p, [0, 1]):
                entity_dofs[0][2].append(i)
            # DOFs associated with edges
            elif np.isclose(p[1], 0):
                entity_dofs[1][0].append(i)
            elif np.isclose(p[1] - p[0], 1):
                entity_dofs[1][1].append(i)
            elif np.isclose(p[1] + p[0], 1):
                entity_dofs[1][2].append(i)
            # DOFs associated with interior of cell
            else:
                entity_dofs[2][0].append(i)
        # </verify4>

        # <verify5>
        def tabulate(points):
            mapped_points = np.array([[2 * p[0] + p[1] - 1, p[1]] for p in points])
            table = np.zeros([points.shape[0], 1, degree])

            for i, p in enumerate(mapped_points):
                for j in range(degree):
                    table[i, 0, j] = e.evaluate(j, p)[0]
            return table

        # </verify5>

        # <verify6>
        return entity_dofs, tabulate

    # </verify6>

    # <variables>
    id = "simplefem"
    name = "simplefem"
    url = "https://github.com/DefElement/simplefem"
    languages = ["python"]
    # </variables>
    # <verificationvariable>
    verification = True


# </verificationvariable>


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
