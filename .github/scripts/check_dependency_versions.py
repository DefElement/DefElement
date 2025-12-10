"""Check that dependencies are up to date."""

import json
import os
import requests


class DependenciesNeedUpdating(BaseException):
    pass


requirements = {}
with open(
    os.path.join(
        os.path.join(
            os.path.join(os.path.dirname(os.path.realpath(__file__)), ".."),
            "..",
        ),
        "requirements.txt",
    )
) as f:
    for line in f:
        lib, version = line.strip().split("==")
        requirements[lib] = version

need_updating = {}
for lib, version in requirements.items():
    latest = requests.get(f"https://pypi.org/pypi/{lib}/json").json()["info"]["version"]
    if version != latest:
        need_updating[lib] = latest

if len(need_updating) > 0:
    for lib, latest in need_updating.items():
        print(f"{lib} can be updated from {requirements[lib]} to {latest}")
    raise DependenciesNeedUpdating()
