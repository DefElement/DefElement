"""Install all supported implementations."""

import argparse
import os

from defelement import implementations

parser = argparse.ArgumentParser(description="Install implementations")
parser.add_argument("--install-type", default="all", help="Type of installation.")
args = parser.parse_args()

if args.install_type not in ["all", "verification"]:
    raise RuntimeError(f"Unknown install type: {args.install_type}")

for i in implementations.implementations.values():
    if args.install_type == "all" or (args.install_type == "verification" and i.verification):
        lang = i.languages[0] if len(i.languages) == 1 else i.install_language
        assert lang is not None
        cmd = i.install(lang)
        assert cmd is not None
        assert os.system(cmd) == 0
