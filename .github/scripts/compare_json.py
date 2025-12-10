"""Check if two JSON files contain the same data."""

import argparse
import json

parser = argparse.ArgumentParser(description="Check if two JSON files contain the same data")
parser.add_argument(
    "files",
    metavar="files",
    nargs=2,
    default=None,
    help="Names of input json files.",
)

args = parser.parse_args()

with open(args.files[0]) as f:
    data0 = json.load(f)
with open(args.files[1]) as f:
    data1 = json.load(f)


def is_equal(a, b):
    if isinstance(a, dict):
        if not isinstance(b, dict) or len(a) != len(b):
            return False
        for ai, aj in a.items():
            if ai not in b or not is_equal(aj, b[ai]):
                return False
        return True
    elif isinstance(a, list):
        if not isinstance(b, list) or len(a) != len(b):
            return False
        for ai, bi in zip(a, b):
            if not is_equal(ai, bi):
                return False
        return True

    return a == b


assert is_equal(data0, data1)
