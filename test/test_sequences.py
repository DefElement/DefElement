import os
import re
import signal
import urllib.request
import warnings

import pytest
import symfem
import sympy
import yaml

oeis_cache = {}


class TimeOutTheTest(BaseException):
    pass


def handler(signum, frame):
    raise TimeOutTheTest()


def latex_to_pyth(formula):
    formula = re.sub(r"([0-9])\(", r"\1*(", str(formula))
    formula = re.sub(r"([0-9])k", r"\1*k", str(formula))
    formula = formula.replace(")(", ")*(")
    formula = formula.replace("k(", "k*(")
    formula = formula.replace("^", "**")
    formula = formula.replace("/", "//")
    return formula


def check_formula(formula, seq):
    if isinstance(formula, list):
        parts = []
        for i, fpart in enumerate(formula):
            k, j = list(fpart.items())[0]
            if "=" in k:
                ns = [int(a) for a in k.split("=")[1].split(",")]
            elif ">=" in k:
                ns = [a for a in seq if a >= int(k.split(">=")[1])]
            elif ">" in k:
                ns = [a for a in seq if a > int(k.split(">")[1])]
            parts.append((j, ns))
        for k, s in seq.items():
            for i, j in parts:
                if k in j:
                    assert s == eval(latex_to_pyth(i).replace("k", str(k)))
                    break
            else:
                warnings.warn(f"k={k} is not included in this sequence")
    else:
        for k, s in seq.items():
            assert s == eval(latex_to_pyth(formula).replace("k", str(k)))


def is_satisfied(condition, n):
    if condition.startswith("k>="):
        return n >= int(condition[3:])
    if condition.startswith("k<="):
        return n <= int(condition[3:])
    if condition.startswith("k>"):
        return n > int(condition[2:])
    if condition.startswith("k<"):
        return n < int(condition[2:])
    raise ValueError


def check_oeis(oeis, seq):
    if " [" in oeis:
        oeis, condition = oeis.split(" [")
        condition = condition.split("]")[0]
        seq = {i: j for i, j in seq.items() if is_satisfied(condition, i)}
    seq = {i: j for i, j in seq.items() if j > 0}
    if oeis not in oeis_cache:
        with urllib.request.urlopen(urllib.request.Request(
            f"http://oeis.org/{oeis}/list", headers={"User-Agent": "DefElement test runner"}
        )) as f:
            oeis_cache[oeis] = "".join([
                i.strip() for i in f.read().decode('utf-8').split(
                    "<pre>[")[1].split("]</pre>")[0].split("\n")])
    assert ",".join([str(i) for i in seq.values()]) in oeis_cache[oeis]


def parse_degree(degree, cellname):
    if isinstance(degree, dict):
        return parse_degree(degree[cellname], cellname)
    if isinstance(degree, str):
        return int(sympy.S(degree).subs("d", symfem.create_reference(cellname).tdim))

    return degree


element_path = os.path.join(os.path.dirname(os.path.realpath(__file__)), "../elements")

inputs = []
for i in os.listdir(element_path):
    if i.endswith(".def"):
        with open(os.path.join(element_path, i)) as f:
            data = yaml.load(f, Loader=yaml.FullLoader)
        inputs += [(i, c) for c in data["reference-elements"]]


@pytest.mark.parametrize("file, cellname", inputs)
def test_sequence(file, cellname):
    if cellname == "dual polygon":
        pytest.skip()
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "implementations" not in data or "symfem" not in data["implementations"]:
        pytest.skip()
    if "ndofs" not in data:
        pytest.skip()

    if isinstance(data["implementations"]["symfem"], dict):
        if cellname not in data["implementations"]["symfem"]:
            pytest.skip()
        symfem_name = data["implementations"]["symfem"][cellname]
    else:
        symfem_name = data["implementations"]["symfem"]

    seq = {}
    if "min-degree" in data:
        mink = parse_degree(data["min-degree"], cellname)
    else:
        mink = 0
    maxk = 10
    if "max-degree" in data:
        maxk = min(maxk, parse_degree(data["max-degree"], cellname))

    for k in range(mink, maxk + 1):
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(25)
            if "variant=" in symfem_name:
                elementname, variant = symfem_name.split(" variant=")
                term = symfem.create_element(cellname, elementname, k, variant=variant).space_dim
            else:
                term = symfem.create_element(cellname, symfem_name, k).space_dim
            seq[k] = term
        except NotImplementedError:
            pass
        except ValueError:
            pass
        except TimeOutTheTest:
            break

    signal.alarm(0)

    if cellname in data["ndofs"]:
        if "formula" in data["ndofs"][cellname]:
            check_formula(data["ndofs"][cellname]["formula"], seq)
        if "oeis" in data["ndofs"][cellname]:
            check_oeis(data["ndofs"][cellname]["oeis"], seq)


@pytest.mark.parametrize("file, cellname", inputs)
def test_entity_sequences(file, cellname):
    if cellname == "dual polygon":
        pytest.skip()
    with open(os.path.join(element_path, file)) as f:
        data = yaml.load(f, Loader=yaml.FullLoader)

    if "implementations" not in data or "symfem" not in data["implementations"]:
        pytest.skip()
    if "entity-ndofs" not in data:
        pytest.skip()

    if isinstance(data["implementations"]["symfem"], dict):
        if cellname not in data["implementations"]["symfem"]:
            pytest.skip()
        symfem_name = data["implementations"]["symfem"][cellname]
    else:
        symfem_name = data["implementations"]["symfem"]

    seq = {"vertices": {}, "edges": {}, "faces": {}, "volumes": {},
           "cell": {}, "facets": {}, "ridges": {}, "peaks": {}}
    if "min-degree" in data:
        mink = parse_degree(data["min-degree"], cellname)
    else:
        mink = 0
    maxk = 10
    if "max-degree" in data:
        maxk = min(maxk, parse_degree(data["max-degree"], cellname))

    for k in range(mink, maxk + 1):
        try:
            signal.signal(signal.SIGALRM, handler)
            signal.alarm(25)
            if "variant=" in symfem_name:
                elementname, variant = symfem_name.split(" variant=")
                e = symfem.create_element(cellname, elementname, k, variant=variant)
            else:
                e = symfem.create_element(cellname, symfem_name, k)
            for d, e_name in zip(range(e.reference.tdim),
                                 ["vertices", "edges", "faces", "volumes"]):
                seq[e_name][k] = len(e.entity_dofs(d, 0))
            for co_d, e_name in zip(range(e.reference.tdim),
                                    ["cell", "facets", "ridges", "peaks"]):
                seq[e_name][k] = len(e.entity_dofs(e.reference.tdim - co_d, 0))
        except NotImplementedError:
            pass
        except TimeOutTheTest:
            break

    signal.alarm(0)

    def run_entity_test(data):
        if isinstance(data, list):
            for i in data:
                run_entity_test(i)
        else:
            for entity in data:
                if "formula" in data[entity]:
                    check_formula(data[entity]["formula"], seq[entity])
                if "oeis" in data[entity]:
                    check_oeis(data[entity]["oeis"], seq[entity])

    if "entity-ndofs" in data:
        run_entity_test(data["entity-ndofs"])
