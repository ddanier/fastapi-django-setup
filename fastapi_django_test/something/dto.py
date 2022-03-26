from fastapi_django_test.something.models import Something
from fastapi_django_test.utils.models.django import django_to_pydantic_model


class SomethingDTO(django_to_pydantic_model(Something)):
    pass
