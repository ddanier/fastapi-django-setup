from fastapi_django_test.utils.namings import to_lower_camel, to_upper_camel


def test_to_lower_camel():
    assert to_lower_camel("foo_bar") == "fooBar"
    assert to_lower_camel("foo_bar_camelCase") == "fooBarCamelcase"


def testto_upper_camel():
    assert to_upper_camel("foo_bar") == "FooBar"
    assert to_upper_camel("foo_bar_camelCase") == "FooBarCamelcase"
