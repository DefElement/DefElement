"""Install all supported implementations."""

import argparse
import os

from defelement import implementations

parser = argparse.ArgumentParser(description="Install implementations")
parser.add_argument("--install-type", default="all", help="Type of installation.")
args = parser.parse_args()

if args.install_type == "all":
    for i in implementations.implementations.values():
        lang = i.languages[0] if len(i.languages) == 1 else i.install_language
        assert i.install(lang) is not None
        assert os.system(i.install(lang)) == 0
elif args.install_type == "verification":
    for i in implementations.implementations.values():
        if i.verification:
            lang = i.languages[0] if len(i.languages) == 1 else i.install_language
            assert i.install(lang) is not None
            assert os.system(i.install(lang)) == 0
else:
    raise RuntimeError(f"Unknown install type: {args.install_type}")
