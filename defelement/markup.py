"""Markup."""

import re
import typing

import symfem

from defelement import plotting
from webtools.markup import markup as _markup
from webtools.markup import insert_links as _insert_links

page_references: typing.List[str] = []


def markup(content: str) -> str:
    """Markup content.

    Args:
        content: Content

    Returns:
        Content with markup replaced by HTML
    """
    return _markup(
        content,
        [(r"{{plot::([^,]+),([^,]+),([0-9]+)}}", plot_element),
         (r"{{plot::([^,]+),([^,]+),([0-9]+)::([0-9]+)}}", plot_single_element),
         (r"{{reference::([^}]+)}}", plot_reference),
         (r"{{img::([^}]+)}}", plot_img)],
        [("{{tick}}", "<i class='fa-solid fa-check' style='color:#55ff00'></i>")],
        insert_links,
    )


def insert_links(txt: str) -> str:
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
    return _insert_links(txt)


def plot_element(matches: typing.Match[str]) -> str:
    """Plot element.

    Args:
        matches: Element data

    Returns:
        HTML for plot of element
    """
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
    else:
        e = symfem.create_element(matches[1], matches[2], int(matches[3]))
    return ("<center>"
            f"{''.join([plotting.plot_function(e, i) for i in range(e.space_dim)])}"
            "</center>")


def plot_single_element(matches: typing.Match[str]) -> str:
    """Plot a single element.

    Args:
        matches: Element data

    Returns:
        HTML for plot of element
    """
    if "variant=" in matches[1]:
        a, b = matches[1].split(" variant=")
        e = symfem.create_element(a, matches[2], int(matches[3]), b)
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
