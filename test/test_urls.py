"""Check URLs against the element definitions."""

from pathlib import Path

import pytest
import yaml

from defelement import get_urls


def test_fiat_urls():
    """Deduplicate cell and variant records without losing distinct pages."""
    urls = get_urls("fiat")
    assert urls["RaviartThomas"] == ("https://defelement.org/elements/raviart-thomas.html",)
    assert urls["Lagrange"] == (
        "https://defelement.org/elements/lagrange.html",
        "https://defelement.org/elements/p1-iso-p2.html",
    )
    assert urls["HsiehCloughTocher"] == (
        "https://defelement.org/elements/hsieh-clough-tocher.html",
        "https://defelement.org/elements/reduced-hsieh-clough-tocher.html",
    )
    assert urls["ArnoldWinther"] == ("https://defelement.org/elements/arnold-winther.html",)


def test_unknown_names():
    """Distinguish unrecorded identifiers from unknown libraries."""
    assert "not-a-FIAT-class" not in get_urls("fiat")
    with pytest.raises(KeyError, match="No implementations recorded"):
        get_urls("not-a-library")


def test_basix_urls():
    """Resolve continuous and discontinuous elements sharing an enum name."""
    basix = get_urls("basix")
    assert basix["P"] == (
        "https://defelement.org/elements/discontinuous-lagrange.html",
        "https://defelement.org/elements/lagrange.html",
    )


def test_symfem_urls():
    """Resolve identifiers containing spaces."""
    assert get_urls("symfem")["discontinuous Lagrange"] == (
        "https://defelement.org/elements/discontinuous-lagrange.html",
    )


def test_all_definitions():
    """Expose every documented implementation using its canonical page URL."""
    expected: dict[str, set[str]] = {}
    element_path = Path(__file__).resolve().parent.parent / "elements"
    for path in element_path.glob("*.def"):
        data = yaml.safe_load(path.read_text())
        for library in data.get("implementations", {}):
            expected.setdefault(library, set()).add(
                f"https://defelement.org/elements/{path.stem}.html"
            )
    for library, urls in expected.items():
        assert {url for matches in get_urls(library).values() for url in matches} == urls
