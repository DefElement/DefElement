"""Bempp-cl implementation."""

import typing

from defelement.implementations.core import Element, Implementation, parse_example


class BemppClImplementation(Implementation):
    """Bempp-cl implementation."""

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
        return f'"{string}"'

    @staticmethod
    def example(element: Element) -> str:
        """Generate examples.

        Args:
            element: The element

        Returns:
            Example code
        """
        out = "import bempp_cl.api"
        out += "\n"
        out += "grid = bempp_cl.api.shapes.regular_sphere(1)"
        for e in element.examples:
            ref, deg, variant, kwargs = parse_example(e)
            assert len(kwargs) == 0

            try:
                bempp_name, input_deg, params = element.get_implementation_string(
                    "bempp-cl", ref, deg, variant
                )
            except NotImplementedError:
                continue

            out += "\n\n"
            out += f"# Create {element.name} degree {deg}\n"
            out += "element = bempp_cl.api.function_space(grid, "
            out += f'"{bempp_name}", {input_deg})'
        return out

    id = "bempp-cl"
    name = "Bempp-cl"
    url = "https://github.com/bempp/bempp-cl"
    install = "pip3 install numba scipy meshio\npip3 install bempp-cl"
