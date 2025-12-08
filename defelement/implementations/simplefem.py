"""Simplefem implementation."""

import typing

from defelement.implementations.core import (
    Array,
    Element,
    Implementation,
    parse_example,
)


class SimplefemImplementation(Implementation):
    """Simplefem implementation."""

    @staticmethod
    def format(
        string: typing.Optional[str], params: typing.Dict[str, typing.Any]
    ) -> str:
        """Format implementation string.

        Args:
            string: Implementation string
            params: Parameters

        Returns:
            Formatted implementation string
        """
        assert string is not None
        return string

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import simplefem"
        for e in element.examples:
            ref, degree, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0

            try:
                name, input_degree, params = element.get_implementation_string(
                    "simplefem", ref, degree, variant
                )
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {degree} on a {ref}\n"
            out += f"element = simplefem.{name}({input_degree})"
        return out

    @staticmethod
    def verify(
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
        import simplefem
        import numpy as np

        assert name == "lagrange_element"

        e = simplefem.lagrange_element(degree)

        ndofs = (degree + 1) * (degree + 2) // 2

        entity_dofs = [[], [], []]
        # DOFs associated with vertices
        entity_dofs[0].append([0])
        entity_dofs[0].append([degree])
        entity_dofs[0].append([ndofs - 1])
        # DOFs associated with edges
        entity_dofs[1].append([])
        entity_dofs[1].append([])
        dof_index = degree + 1
        for i in range(1, degree):
            entity_dofs[1][1].append(dof_index)
            dof_index += degree - i
            entity_dofs[1][0].append(dof_index)
            dof_index += 1
        entity_dofs[1].append(list(range(1, degree)))
        # DOFs associated with interior of cell
        entity_dofs[2].append([])
        dof_start = degree + 2
        for i in range(degree - 2):
            entity_dofs[2][0] += list(range(dof_start, dof_start + degree - 2 - i))
            dof_start += degree - i

        def tabulate(points):
            mapped_points = np.array([[2 * p[0] + p[1] - 1, p[1]] for p in points])
            table = e.tabulate(mapped_points)
            return table.T.reshape([table.shape[1], 1, table.shape[0]])

        return entity_dofs, tabulate

    id = "simplefem"
    name = "simplefem"
    url = "https://github.com/DefElement/simplefem"
    verification = True
    install = "pip3 install git+https://github.com/DefElement/simplefem"
