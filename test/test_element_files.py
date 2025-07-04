import os

import pytest
import yaml

dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../elements")


def parse_contributing_page():
    with open(os.path.join(dir_path, "../CONTRIBUTING.md")) as f:
        table = f.read().split("<table")[1].split(">", 1)[1].split("</table>")[0]
    if "<thead>" in table:
        table = table.split("</thead>")[1]
    table = table.strip()

    docs = {"req": [], "opt": [], "all": []}
    for line in table.split("\n"):
        name = line.split("`")[1].replace("&#8209;", "-")
        docs["all"].append(name)
        if "{{tick}}" in line:
            docs["req"].append(name)
        else:
            docs["opt"].append(name)

    return docs


def test_parse():
    docs = parse_contributing_page()
    assert len(docs["req"]) == len(set(docs["req"]))
    assert len(docs["opt"]) == len(set(docs["opt"]))
    assert len(docs["all"]) == len(set(docs["all"]))
    assert set(docs["all"]) == set(docs["req"] + docs["opt"])


@pytest.mark.parametrize(
    "e", [e for e in os.listdir(element_path) if e.endswith(".def")]
)
def test_element_page(e):
    with open(os.path.join(element_path, e)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    docs = parse_contributing_page()

    for key in data.keys():
        assert key in docs["all"]

    for key in docs["req"]:
        assert key in data


@pytest.mark.parametrize(
    "e", [e for e in os.listdir(element_path) if e.endswith(".def")]
)
def test_symfem_no_degreemap(e):
    def no_degreemap(impl):
        if isinstance(impl, dict):
            return all(no_degreemap(i) for i in impl.values())
        return "DEGREEMAP" not in impl

    with open(os.path.join(element_path, e)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "implementations" in data and "symfem" in data["implementations"]:
        assert no_degreemap(data["implementations"]["symfem"])
