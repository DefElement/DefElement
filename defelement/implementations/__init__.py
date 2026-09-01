"""Implementations."""

import importlib
import os
from inspect import isclass

from defelement.implementations.core import (
    DegreeNotImplemented,
    Implementation,
    NotImplementedOnReference,
    VariantNotImplemented,
    parse_example,
)

__all__ = [
    "DegreeNotImplemented",
    "Implementation",
    "NotImplementedOnReference",
    "VariantNotImplemented",
    "examples",
    "formats",
    "implementations",
    "parse_example",
    "verifications",
]

implementations = {}
this_dir = os.path.dirname(os.path.realpath(__file__))
for file in os.listdir(this_dir):
    if file.endswith(".py") and not file.startswith("_") and file != "core.py":
        mod = importlib.import_module(f"defelement.implementations.{file[:-3]}")
        for name in dir(mod):
            if not name.startswith("_"):
                c = getattr(mod, name)
                if isclass(c) and c != Implementation and issubclass(c, Implementation):
                    implementations[c.id] = c

formats = {id: i.format for id, i in implementations.items()}
examples = {id: i.examples for id, i in implementations.items()}
versions = {id: i.version for id, i in implementations.items()}
verifications = {id: i.verify for id, i in implementations.items() if i.verification}

sorted_ids = list(formats.keys())
sorted_verification_ids = list(verifications.keys())
sorted_ids.sort(key=lambda id: implementations[id].name.lower())
sorted_verification_ids.sort(key=lambda id: implementations[id].name.lower())
