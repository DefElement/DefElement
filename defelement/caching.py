"""Caching."""

import json
import os
import typing

import symfem
from webtools.tools import join

from defelement import settings

cache_version = "1.0.0"


def load_cache(
    item_key: str, e: symfem.finite_element.FiniteElement,
) -> typing.Optional[str]:
    """Load item from cache."""
    try:
        with open(join(settings.cache_path, f"{item_key}.json")) as f:
            data = json.load(f)
        if data.get("symfem_version") != symfem.__version__:
            return None
        if data.get("last_updated") != e.last_updated:
            return None
        if data.get("cache_version") != cache_version:
            return None
        return data.get("content")
    except FileNotFoundError:
        return None


def save_cache(item_key: str, e: symfem.finite_element.FiniteElement, item: str):
    """Save item to cache."""
    if not os.path.isdir(settings.cache_path):
        os.mkdir(settings.cache_path)
    data = {
        "content": item,
        "symfem_version": symfem.__version__,
        "last_updated": e.last_updated,
        "cache_version": cache_version,
    }
    with open(join(settings.cache_path, f"{item_key}.json"), "w") as f:
        return json.dump(data, f)
