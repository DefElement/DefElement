"""Programming languages."""

from webtools.code_markup import python_highlight, rust_highlight, cpp_highlight
from defelement.implementations import Implementation
from inspect import isclass
import sys


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
    def install(cls, impl: Implementation) -> str:
        """Generate installation information for a language.

        Args:
            impl: The implementation

        Returns:
            Installation info
        """
        info = f"Before running this example, you must install <a href='{impl.url}'>{impl.name}</a>"

        cmd = impl.install(cls.name)

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
    def install(cls, impl: Implementation) -> str:
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


this = sys.modules[__name__]

languages = {}

for item in dir():
    lang = getattr(this, item)
    if isclass(lang) and issubclass(lang, Language):
        languages[lang.id] = lang
