import os

import yaml

from defelement.element import Element
from defelement.implementations import parse_example, verifications
from defelement.verification import verify

dir_path = os.path.dirname(os.path.realpath(__file__))
element_path = os.path.join(dir_path, "../elements")


def test_self():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "lagrange")

    eg = [i for i in e.examples if "triangle" in i][0]
    reference, defelement_degree, variant, kwargs = parse_example(eg)
    symfem_name, symfem_degree, symfem_params = e.get_implementation_string(
        "symfem",
        reference,
        defelement_degree,
        variant,
    )

    info = verifications["symfem"](
        symfem_name, reference, symfem_degree, symfem_params, e, eg
    )
    assert verify("triangle", info, info)[0]


def test_variant():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "lagrange")

    eg0, eg1 = [i for i in e.examples if "quadrilateral,1" in i][:2]

    reference0, defelement_degree0, variant0, kwargs0 = parse_example(eg0)
    symfem_name0, symfem_degree0, symfem_params0 = e.get_implementation_string(
        "symfem",
        reference0,
        defelement_degree0,
        variant0,
    )

    reference1, defelement_degree1, variant1, kwargs1 = parse_example(eg1)
    symfem_name1, symfem_degree1, symfem_params1 = e.get_implementation_string(
        "symfem",
        reference1,
        defelement_degree1,
        variant1,
    )

    info0 = verifications["symfem"](
        symfem_name0, reference0, symfem_degree0, symfem_params0, e, eg0
    )
    info1 = verifications["symfem"](
        symfem_name1, reference1, symfem_degree1, symfem_params1, e, eg1
    )

    assert verify("quadrilateral", info0, info1)[0]


def test_hermite_vs_lagrange():
    with open(os.path.join(element_path, "lagrange.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "lagrange")
    eg = [i for i in e.examples if "triangle,3" in i][0]
    reference, defelement_degree, variant, kwargs = parse_example(eg)
    symfem_name, symfem_degree, symfem_params = e.get_implementation_string(
        "symfem",
        reference,
        defelement_degree,
        variant,
    )
    info0 = verifications["symfem"](
        symfem_name, reference, symfem_degree, symfem_params, e, eg
    )

    with open(os.path.join(element_path, "hermite.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e = Element(data, "hermite")
    eg = [i for i in e.examples if "triangle,3" in i][0]
    reference, defelement_degree, variant, kwargs = parse_example(eg)
    symfem_name, symfem_degree, symfem_params = e.get_implementation_string(
        "symfem",
        reference,
        defelement_degree,
        variant,
    )
    info1 = verifications["symfem"](
        symfem_name, reference, symfem_degree, symfem_params, e, eg
    )

    assert not verify("triangle", info0, info1)[0]


def test_verify_bdm_vs_n2():
    with open(os.path.join(element_path, "brezzi-douglas-marini.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e0 = Element(data, "brezzi-douglas-marini")
    with open(os.path.join(element_path, "nedelec2.def")) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)
    e1 = Element(data, "nedelec2")

    eg = [i for i in e0.examples if i in e1.examples and "triangle" in i][0]

    reference, defelement_degree, variant, kwargs = parse_example(eg)
    symfem_name0, symfem_degree0, symfem_params0 = e0.get_implementation_string(
        "symfem",
        reference,
        defelement_degree,
        variant,
    )
    symfem_name1, symfem_degree1, symfem_params1 = e1.get_implementation_string(
        "symfem",
        reference,
        defelement_degree,
        variant,
    )

    info0 = verifications["symfem"](
        symfem_name0, reference, symfem_degree0, symfem_params0, e0, eg
    )
    info1 = verifications["symfem"](
        symfem_name1, reference, symfem_degree1, symfem_params1, e1, eg
    )
    assert not verify("triangle", info0, info1)[0]
