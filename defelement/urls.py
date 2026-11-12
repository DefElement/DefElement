"""DefElement page URLs indexed by implementation identifier."""

from importlib.metadata import distribution
from pathlib import Path

import yaml


def get_urls(library: str) -> dict[str, tuple[str, ...]]:
    """Get DefElement URLs for a library's implementation names.

    Args:
        library: Implementation ID, such as "fiat" or "basix".

    Returns:
        Implementation names mapped to sorted, unique URL tuples.

    Raises:
        KeyError: If the library has no recorded implementations.
    """
    element_files = Path(__file__).resolve().parent.parent / "elements"
    if element_files.is_dir():
        paths = element_files.glob("*.def")
    elif any(element_files.parent.glob("*.def")):
        paths = element_files.parent.glob("*.def")
    else:
        package = distribution("defelement")
        paths = (
            Path(str(package.locate_file(path)))
            for path in package.files or []
            if path.suffix == ".def"
        )

    urls: dict[str, set[str]] = {}
    for path in sorted(paths, key=lambda p: p.name):
        if path.name.startswith("."):
            continue
        data = yaml.safe_load(path.read_text(encoding="utf-8"))
        implementations = data.get("implementations", {})
        if library not in implementations:
            continue
        url = f"https://defelement.org/elements/{path.name[:-4]}.html"
        for variant in data.get("variants", {None: {}}):
            implementation = implementations[library]
            if variant is not None:
                if variant not in implementation:
                    continue
                implementation = implementation[variant]
            if isinstance(implementation, str):
                implementation = {None: implementation}
            for reference, name in implementation.items():
                if reference == "display":
                    continue
                if "=" in name:
                    name = " ".join(name.split("=", 1)[0].split(" ")[:-1])
                urls.setdefault(name, set()).add(url)

    if not urls:
        raise KeyError(f"No implementations recorded for library: {library}")
    return {identifier: tuple(sorted(matches)) for identifier, matches in urls.items()}
