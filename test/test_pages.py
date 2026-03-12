import os

import pytest

dir_path = os.path.dirname(os.path.realpath(__file__))
pages_path = os.path.join(dir_path, "../pages")

md_files = [p for p in os.listdir(pages_path) if p.endswith(".md")]


@pytest.mark.parametrize("p", md_files)
def test_brackets(p):
    with open(os.path.join(pages_path, p)) as f:
        page = f.read()

    assert page.count("(") == page.count(")")
