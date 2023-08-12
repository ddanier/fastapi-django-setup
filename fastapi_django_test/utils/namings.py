import re

UPPERCASE_RE = re.compile(r"(?<!^)(?=[A-Z])")


def to_camel_case(string: str) -> str:
    """Convert 'foo_bar' to 'fooBar'."""

    return "".join(
        (
            word.capitalize()
            if i > 0
            else word.lower()
        )
        for i, word
        in enumerate(string.split("_"))
    )


def to_pascal_case(string: str) -> str:
    """Convert 'foo_bar' to 'FooBar'."""

    return "".join(
        word.capitalize()
        for word
        in string.split("_")
    )


def to_snake_case(string: str) -> str:
    """Convert 'FooBar' or 'fooBar' to 'foo_bar'."""

    return "_".join(
        word.lower()
        for word
        in UPPERCASE_RE.split(string)
    )
