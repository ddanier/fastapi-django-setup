from fastapi_django_test.utils.namings import to_camel_case, to_pascal_case, to_snake_case


def test_to_camel_case():
    assert to_camel_case("foo_bar") == "fooBar"
    assert to_camel_case("foo_bar_camelCase") == "fooBarCamelcase"
    assert to_camel_case("some_db_thingy") == "someDbThingy"  # cannot be done right
    assert to_camel_case("some_d_b_thingy") == "someDBThingy"


def test_to_pascal_case():
    assert to_pascal_case("foo_bar") == "FooBar"
    assert to_pascal_case("foo_bar_camelCase") == "FooBarCamelcase"
    assert to_pascal_case("some_db_thingy") == "SomeDbThingy"  # cannot be done right
    assert to_pascal_case("some_d_b_thingy") == "SomeDBThingy"


def test_to_snake_case():
    assert to_snake_case("FooBar") == "foo_bar"
    assert to_snake_case("fooBar") == "foo_bar"
    assert to_snake_case("foo_bar_camelCase") == "foo_bar_camel_case"
    assert to_snake_case("SomeDBThingy") == "some_d_b_thingy"  # cannot be done right
