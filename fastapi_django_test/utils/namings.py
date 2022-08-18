def to_lower_camel(string: str) -> str:
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


def to_upper_camel(string: str) -> str:
    """Convert 'foo_bar' to 'FooBar'."""

    return "".join(
        word.capitalize()
        for word
        in string.split("_")
    )

