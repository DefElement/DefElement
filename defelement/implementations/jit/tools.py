"""Utility functions."""

import shutil
import traceback
from datetime import datetime
import hashlib
import os
from appdirs import user_cache_dir
try:
    os.mkdir(user_cache_dir())
except FileExistsError:
    pass

TODAY = datetime.now().strftime("%Y-%m-%d")
DIR = user_cache_dir("defelement")
try:
    os.mkdir(DIR)
except FileExistsError:
    pass


def source_dir(language: str, id: str | None) -> str:
    """Get directory for source in cache directory."""
    if id is None:
        n = 0
        while os.path.isdir(os.path.join(DIR, f"{language}-{n}")):
            n += 1
        folder = os.path.join(DIR, f"{language}-{n}")
    else:
        folder = os.path.join(DIR, f"{language}-" + hash(id))

    if os.path.isfile(os.path.join(folder, ".error")):
        with open(os.path.join(folder, ".error")) as f:
            date = f.read().split("\n")[0]
        if date != TODAY:
            shutil.rmtree(folder)
    check_for_error(folder)
    if not os.path.isdir(folder):
        os.mkdir(folder)
    return folder


def save_error(folder: str, error: BaseException):
    """Save an error message into the source directory."""
    with open(os.path.join(folder, ".error"), "w") as f:
        f.write(f"{TODAY}\n\n{traceback.format_exc()}")


def check_for_error(folder: str):
    """Check for an error message in the source directory."""
    if os.path.isfile(os.path.join(folder, ".error")):
        raise RuntimeError(f"Error building C++ code. See {folder}/.error for details")


def hash(text: str) -> str:
    return hashlib.sha256(text.encode('utf-8')).hexdigest()

