"""Install all supported implementations."""

import argparse
import os

from defelement import implementations, settings
from defelement.element import Categoriser

parser = argparse.ArgumentParser(description="Install implementations")
parser.add_argument("--install-type", default="all", help="Type of installation.")
args = parser.parse_args()

if args.install_type not in ["all", "verification"]:
    raise RuntimeError(f"Unknown install type: {args.install_type}")

# Load elements from .def files to find the additional packages each implementation needs
categoriser = Categoriser()
categoriser.load_references(os.path.join(settings.data_path, "references"))
categoriser.load_families(os.path.join(settings.data_path, "families"))
categoriser.load_folder(settings.element_path)

for i in implementations.implementations.values():
    if args.install_type == "all" or (args.install_type == "verification" and i.verification):
        lang = i.languages[0] if len(i.languages) == 1 else i.install_language
        assert lang is not None
        dependencies = sorted(
            {d for e in categoriser.elements for d in e.implementation_dependencies(i.id)}
        )
        cmd = i.install(lang, dependencies)
        assert cmd is not None
        assert os.system(cmd) == 0
