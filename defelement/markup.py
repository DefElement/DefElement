"""Markup."""

import re
import typing

import symfem
from webtools import settings
from webtools.markup import insert_links as _insert_links
from webtools.code_markup import code_highlight as _code_highlight

from defelement import info, plotting, symbols, citations

page_references: typing.List[str] = []


def insert_links(txt: str, root_dir: str = "") -> str:
    """Insert links.

    Args:
        txt: text

    Returns:
        Text with links
    """
    txt = re.sub(r"\(element::([^\)]+)\)", r"(/elements/\1.html)", txt)
    txt = re.sub(r"\(reference::([^\)]+)\)", r"(/lists/references/\1.html)", txt)
    txt = txt.replace("(index::all)", "(/elements/index.html)")
    txt = txt.replace("(index::families)", "(/families/index.html)")
    txt = txt.replace("(index::recent)", "(/lists/recent.html)")
    txt = re.sub(r"\(index::([^\)]+)::([^\)]+)\)", r"(/lists/\1/\2.html)", txt)
    txt = re.sub(r"\(index::([^\)]+)\)", r"(/lists/\1)", txt)
    return _insert_links(txt, root_dir)


def plot_element(matches: typing.Match[str]) -> str:
    """Plot element.

    Args:
        matches: Element data

    Returns:
        HTML for plot of element
    """
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), variant=b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))

    return (
        "<center>"
        f"{''.join([plotting.plot_function(e, i) for i in range(e.space_dim)])}"
        "</center>"
    )


def plot_single_element(matches: typing.Match[str]) -> str:
    """Plot a single element.

    Args:
        matches: Element data

    Returns:
        HTML for plot of element
    """
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), variant=b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))

    return f"<center>{plotting.plot_function(e, int(matches[4]))}</center>"


def plot_reference(matches: typing.Match[str]) -> str:
    """Plot references.

    Args:
        matches: Reference data

    Returns:
        HTML
    """
    e = symfem.create_reference(matches[1])
    return f"<center>{plotting.plot_reference(e)}</center>"


def plot_img(matches: typing.Match[str]) -> str:
    """Plot an image.

    Args:
        matches: Image info

    Returns:
        HTML for image
    """
    e = matches[1]
    return f"<center>{plotting.plot_img(e)}</center>"


def insert_citation(matches: typing.Match[str]) -> str:
    """Insert a citation.

    Args:
        matches: Citation info

    Returns:
        HTML for citation
    """
    id = matches[1]
    return (
        "<ref "
        + " ".join(f'{i}="{j}"' for i, j in getattr(citations, id).items())
        + ">"
    )


def insert_snippet(matches: typing.Match[str]) -> str:
    """Insert a snippet.

    Args:
        matches: Snippet info

    Returns:
        HTML for snippet
    """
    file = matches[1]
    tag = matches[2]
    with open(file) as f:
        content = f.read().split(f"# <{tag}>\n")[1].split(f"# </{tag}>\n")[0]
    out = ""
    for part in re.split(r"\n\n+", content.rstrip(" \n").lstrip("\n")):
        out += "<p class='pcode'>"
        if file.endswith(".py"):
            out += _code_highlight(part, "python")
        else:
            out += _code_highlight(part)
        out += "</p>"
    return out


settings.re_extras = [
    (r"{{plot::([^,]+),([^,]+),([0-9]+)}}", plot_element),
    (r"{{plot::([^,]+),([^,]+),([0-9]+)::([0-9]+)}}", plot_single_element),
    (r"{{reference::([^}]+)}}", plot_reference),
    (r"{{img::([^}]+)}}", plot_img),
    (
        r"{{symbols\.([^}\(]+)\(([0-9]+)\)}}",
        lambda m: getattr(symbols, m[1])(int(m[2])),
    ),
    (r"{{symbols\.([^}]+)}}", lambda m: getattr(symbols, m[1])),
    (r"{{citation::([^}]+)}}", insert_citation),
    (r"{{snippet::([^:]*)::([A-Za-z0-9\-]+)}}", insert_snippet),
]
settings.str_extras = [
    ("{{tick}}", "<i class='fa-solid fa-check' style='color:#55ff00'></i>"),
    ("{{number-of-elements}}", f"{info.number_of_elements}"),
]
settings.insert_links = insert_links
