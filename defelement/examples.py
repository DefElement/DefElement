"""Examples."""

import os
import typing

import sympy
from symfem.finite_element import CiarletElement, DirectElement, FiniteElement
from symfem.functionals import BaseFunctional
from symfem.functions import Function
from symfem.piecewise_functions import PiecewiseFunction
from symfem.symbols import t
from webtools.html import make_html_forwarding_page, make_html_page
from webtools.markup import heading_with_self_ref

from defelement import plotting, settings, symbols
from defelement.caching import load_cache, save_cache

defelement_t = ["s_{0}", "s_{1}", "s_{2}"]


def to_tex(
    f: typing.Union[
        Function,
        sympy.core.expr.Expr,
        typing.List[typing.Union[Function, sympy.core.expr.Expr]],
        typing.Tuple[typing.Union[Function, sympy.core.expr.Expr], ...],
    ],
    tfrac: bool = False,
) -> str:
    """Convert function to TeX.

    Args:
        f: A function
        tfrac: Should tfrac be used in the place of frac?

    Returns:
        TeX
    """
    if isinstance(f, PiecewiseFunction):
        sub_f = None
        for p in f.pieces.values():
            if sub_f is None:
                sub_f = p
            if p != sub_f:
                break
        else:
            return to_tex(sub_f)

    if isinstance(f, (list, tuple)):
        return (
            "\\left(\\begin{array}{c}"
            + "\\\\".join(["\\displaystyle " + to_tex(i) for i in f])
            + "\\end{array}\\right)"
        )
    elif isinstance(f, Function):
        out = f.as_tex()
    else:
        out = sympy.latex(sympy.simplify(sympy.expand(f)))
        out = out.replace("\\left[", "\\left(")
        out = out.replace("\\right]", "\\right)")

        for i, j in zip(t, defelement_t):
            out = out.replace(sympy.latex(i), j)

    if tfrac:
        return out.replace("\\frac", "\\tfrac")
    else:
        return out


def entity_name(dim: int) -> str:
    """Get the name of a sub-entity.

    Args:
        dim: The dimension

    Returns:
        Sub-entity name
    """
    return ["vertex", "edge", "face", "volume"][dim]


def describe_dof(
    element: FiniteElement, d: BaseFunctional
) -> typing.Tuple[str, typing.List[str]]:
    """Describe a DOF.

    Args:
        element: The element
        d: The DOF

    Returns:
        Formatted DOF, and list of symbols included in definition
    """
    desc, symb = d.get_tex()

    for i, j in zip(t, defelement_t):
        desc = desc.replace(sympy.latex(i), j)

    for j in defelement_t:
        if j in desc:
            dim = element.reference.tdim
            new_s = "\\("
            if dim == 1:
                new_s += defelement_t[0]
            else:
                new_s += ",".join(defelement_t[:dim])
            new_s += f"\\) is a parametrisation of \\({d.entity_tex()}\\)"
            symb.append(new_s)
            break

    return desc, symb


def markup_example(
    element: FiniteElement,
    html_name: str,
    element_page: str,
    fname: str,
    legacy_filenames: typing.List[str] = [],
) -> str:
    """Markup examples.

    Args:
        element: The element
        html_name: Name of element
        element_page: URL of elemtn page
        fname: Filename
        legacy_filenames: Old filenames to create redirects from

    Returns:
        Example as HTML
    """
    eg = heading_with_self_ref(
        "h1", f"Degree {element.order} {html_name} on a {element.reference.name}"
    )
    eg += "\n"
    eg += f"<a href='{element_page}'><small>&#9664; Back to {html_name} definition page"
    eg += "</a></small>\n"
    eg += "<center>" + plotting.plot_dof_diagram(element) + "</center>\n"
    eg += "In this example:\n<ul>\n"
    # Reference
    eg += f"<li>\\({symbols.reference}\\) is the reference {element.reference.name}."
    eg += " The following numbering of the subentities of the reference cell is used:</li>\n"
    eg += "<center>" + plotting.plot_reference(element.reference) + "</center>\n"
    if isinstance(element, CiarletElement) and element.reference.name != "dual polygon":
        # Polynomial set
        eg += f"<li>\\({symbols.polyset}\\) is spanned by: "
        eg += ", ".join(
            ["\\(" + to_tex(i) + "\\)" for i in element.get_polynomial_basis()]
        )
        eg += "</li>\n"

        # Dual basis
        eg += f"<li>\\({symbols.dual_basis}=\\{{{symbols.functional}_0,"
        eg += f"...,{symbols.functional}_{{{len(element.dofs) - 1}}}\\}}\\)</li>\n"

    # Basis functions
    if (
        not isinstance(element, CiarletElement)
        or element.reference.name == "dual polygon"
    ):
        eg += "<li>Basis functions:</li>"
    else:
        eg += "<li>Functionals and basis functions:</li>"
    eg += "</ul>"

    plots = plotting.plot_basis_functions(element)

    cache_key = f"markup_example-{html_name}-{element.order}-{element.reference.name}"
    for i, j in element.init_kwargs().items():
        cache_key += f"-{i}-{j}"
    basis = load_cache(cache_key, element.last_updated)

    if basis is None:
        basis = ""
        for dof_i, func in enumerate(element.get_basis_functions()):
            basis += "<div class='basisf'><div style='display:inline-block'>"
            pd = plots[dof_i]
            if pd is not None:
                basis += pd
            basis += "</div>"
            basis += "<div style='display:inline-block;padding-left:10px;padding-bottom:10px'>"
            if isinstance(element, CiarletElement) and len(element.dofs) > 0:
                dof = element.dofs[dof_i]
                basis += f"\\(\\displaystyle {symbols.functional}_{{{dof_i}}}:"
                dof_tex, symbols_used = describe_dof(element, dof)
                basis += dof_tex + "\\)"
                if len(symbols_used) > 0:
                    basis += "<br />where " + ";<br />".join(symbols_used[:-1])
                    if len(symbols_used) > 1:
                        basis += ";<br />and "
                    basis += symbols_used[-1] + "."
                basis += "<br /><br />"
            if element.range_dim == 1:
                basis += f"\\(\\displaystyle {symbols.basis_function}_{{{dof_i}}} = "
            elif element.range_shape is None or len(element.range_shape) == 1:
                basis += (
                    f"\\(\\displaystyle {symbols.vector_basis_function}_{{{dof_i}}} = "
                )
            else:
                basis += (
                    f"\\(\\displaystyle {symbols.matrix_basis_function}_{{{dof_i}}} = "
                )
            basis += to_tex(func) + "\\)"
            if isinstance(element, CiarletElement):
                if len(element.dofs) > 0:
                    basis += "<br /><br />"
                    basis += "This DOF is associated with "
                    basis += entity_name(dof.entity[0]) + f" {dof.entity[1]}"
                    basis += " of the reference cell."
            elif isinstance(element, DirectElement):
                basis += "<br /><br />"
                basis += "This DOF is associated with "
                basis += entity_name(element._basis_entities[dof_i][0])
                basis += f" {element._basis_entities[dof_i][1]}"
                basis += " of the reference cell."
            basis += "</div>"
            basis += "</div>"
        save_cache(cache_key, element.last_updated, basis)

    eg += basis

    with open(
        os.path.join(os.path.join(settings.htmlelement_path, "examples", fname)), "w"
    ) as f:
        f.write(make_html_page(eg))

    for i in legacy_filenames:
        with open(
            os.path.join(os.path.join(settings.htmlelement_path, "examples", i)), "w"
        ) as f:
            f.write(make_html_forwarding_page(f"/elements/examples/{fname}"))

    return f"/elements/examples/{fname}"
