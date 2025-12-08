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
            ref, deg, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0

            try:
                simplefem_name, input_deg, params = element.get_implementation_string(
                    "simplefem", ref, deg, variant
                )
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name_with_variant(variant)} degree {deg} on a {ref}\n"
            out += f"element = simplefem.{simplefem_name}({input_deg})"
        return out

    @staticmethod
    def verify(
        element: Element, example: str
    ) -> typing.Tuple[
        typing.List[typing.List[typing.List[int]]], typing.Callable[[Array], Array]
    ]:
        """Get verification data.

        Args:
            element: Element data
            example: Example data

        Returns:
            List of entity dofs, and tabulation function
        """
        import simplefem
        import numpy as np

        ref, deg, variant, kwargs = parse_example(example)
        assert len(kwargs) == 0
        simplefem_name, deg, params = element.get_implementation_string(
            "simplefem", ref, deg, variant, any_variant=True
        )
        assert deg is not None
        assert simplefem_name == "lagrange_element"

        e = simplefem.lagrange_element(deg)

        ndofs = (deg + 1) * (deg + 2) // 2

        entity_dofs = [[], [], []]
        # DOFs associated with vertices
        entity_dofs[0].append([0])
        entity_dofs[0].append([deg])
        entity_dofs[0].append([ndofs - 1])
        # DOFs associated with edges
        entity_dofs[1].append([])
        entity_dofs[1].append([])
        dof_index = deg + 1
        for i in range(1, deg):
            entity_dofs[1][1].append(dof_index)
            dof_index += deg - i
            entity_dofs[1][0].append(dof_index)
            dof_index += 1
        entity_dofs[1].append(list(range(1, deg)))
        # DOFs associated with interior of cell
        entity_dofs[2].append([])
        dof_start = deg + 2
        for i in range(deg - 2):
            entity_dofs[2][0] += list(range(dof_start, dof_start + deg - 2 - i))
            dof_start += deg - i

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
