"""Simplefem implementation."""

# <intro>
import typing

from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
)


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
    def example_import(cls) -> str:
        """Get imports to include at start of example."""
        return "import simplefem"

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
        return f"element = simplefem.{name}({degree})"

    # </example>

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
    ) -> tuple[list[list[list[int]]], typing.Callable[[Array], Array]]:
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
        entity_dofs = [[[], [], []], [[], [], []], [[]]]

        for i, p in enumerate(e.evaluation_points):
            # DOFs associated with vertices
            if np.allclose(p, [-1, 0]):
                entity_dofs[0][0].append(i)
            elif np.allclose(p, [1, 0]):
                entity_dofs[0][1].append(i)
            elif np.allclose(p, [0, 1]):
                entity_dofs[0][2].append(i)
            # DOFs associated with edges
            elif np.isclose(p[1] + p[0], 1):
                entity_dofs[1][0].append(i)
            elif np.isclose(p[1] - p[0], 1):
                entity_dofs[1][1].append(i)
            elif np.isclose(p[1], 0):
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
                    table[i, 0, j] = e.evaluate(j, p)
            return table

        # </verify5>

        # <verify6>
        return entity_dofs, tabulate

    # </verify6>

    # <variables>
    id = "simplefem"
    name = "simplefem"
    url = "https://github.com/DefElement/simplefem"
    install = "pip3 install git+https://github.com/DefElement/simplefem"
    # </variables>
    # <verificationvariable>
    verification = True


# </verificationvariable>
