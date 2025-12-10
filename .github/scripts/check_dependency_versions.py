"""Check that dependencies are up to date."""

import os
import requests

try:
    import tomllib
except ModuleNotFoundError:  # TODO: remove this once minimum Python version is 3.10
    import tomli as tomllib

green = "\033[32m"
red = "\033[31m"
blue = "\033[34m"
default = "\033[0m"


class DependenciesNeedUpdating(BaseException):
    pass


requirements = {}
with open(
    os.path.join(
        os.path.join(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."),
            "..",
        ),
        "pyproject.toml",
    ),
    "rb",
) as f:
    for dep in tomllib.load(f)["project"]["dependencies"]:
        lib, version = dep.split("==")
        requirements[lib] = version

need_updating = {}
for lib, version in requirements.items():
    latest = requests.get(f"https://pypi.org/pypi/{lib}/json").json()["info"]["version"]
    if version == latest:
        print(f"{green}{lib}{default} is at latest version ({version})")
    else:
        need_updating[lib] = latest
        print(f"{red}{lib}{default} can be updated from {version} to {latest}")

if len(need_updating) > 0:
    raise DependenciesNeedUpdating()
