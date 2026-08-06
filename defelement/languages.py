"""Programming languages."""

import sys
from inspect import isclass

from webtools.code_markup import cpp_highlight, python_highlight, rust_highlight

from defelement.implementations import Implementation


def julia_highlight(code: str) -> str:
    """Highlight comments in a Julia snippet and convert it to HTML.

    webtools does not provide a Julia highlighter. The snippets are short enough that
    keyword highlighting adds little, so only comments are highlighted, using the same
    color that webtools uses.

    Args:
        code: Julia snippet

    Returns:
        Snippet with comments highlighted
    """
    out = []
    for line in code.replace(" ", "&nbsp;").split("\n"):
        if "#" in line:
            line, comment = line.split("#", 1)
            line += f"<span style='color:#FF8800'>#{comment}</span>"
        out.append(line)
    return "<br />".join(out)


class Language:
    """A programming language."""

    @classmethod
    def highlight(cls, code: str) -> str:
        """Add code highlighting.

        Args:
            code: Some code

        Returns:
            Code with HTML formatting
        """
        raise NotImplementedError()

    @classmethod
    def install(cls, impl: type[Implementation]) -> str:
        """Generate installation information for a language.

        Args:
            impl: The implementation

        Returns:
            Installation info
        """
        info = f"Before running this example, you must install <a href='{impl.url}'>{impl.name}</a>"

        cmd = impl.install(cls.id)

        if cmd is None:
            info += ". "
        else:
            info += ":<p class='pcode'>" + cmd.replace("\n", "<br />") + "</p>"
        return info

    # Javascript-friendly id
    id: str
    # Human-readable name of language
    name: str


class Python(Language):
    """Python."""

    @classmethod
    def highlight(cls, code: str) -> str:
        """Add code highlighting."""
        return python_highlight(code)

    id = "python"
    name = "Python"


class Rust(Language):
    """Rust."""

    @classmethod
    def highlight(cls, code: str) -> str:
        """Add code highlighting."""
        return rust_highlight(code)

    @classmethod
    def install(cls, impl: type[Implementation]) -> str:
        """Generate installation information for a language."""
        info = (
            f"To running this snippet, you must add <a href='{impl.url}'>{impl.name}</a>"
            " to your Cargo.toml file"
        )

        cmd = impl.install("rust")

        if cmd is None:
            info += ". "
        else:
            info += ":<p class='pcode'>" + cmd.replace("\n", "<br />") + "</p>"
        return info

    id = "rust"
    name = "Rust"


class Cpp(Language):
    """C++."""

    @classmethod
    def highlight(cls, code: str) -> str:
        """Add code highlighting."""
        return cpp_highlight(code)

    id = "cpp"
    name = "C++"


class Julia(Language):
    """Julia."""

    @classmethod
    def highlight(cls, code: str) -> str:
        """Add code highlighting."""
        return julia_highlight(code)

    id = "julia"
    name = "Julia"


this = sys.modules[__name__]

languages = {}

for item in dir():
    lang = getattr(this, item)
    if isclass(lang) and issubclass(lang, Language) and lang != Language:
        languages[lang.id] = lang
