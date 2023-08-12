from fastapi_django.models import django_to_pydantic_model
from fastapi_django_test.something.models import Something


class SomethingDTO(django_to_pydantic_model(Something)):  # type: ignore
    pass
