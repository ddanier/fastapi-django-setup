import datetime
import decimal
import uuid

import pydantic
from dirty_equals import Contains
from django.db import models

from fastapi_django.models import django_to_pydantic_model
from fastapi_django.models.fields import HAS_EMAIL_VALIDATOR


class Something(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    size = models.FloatField(null=True, blank=True)
    weight = models.DecimalField(null=True, blank=True)
    birth = models.DateField(null=True, blank=True)
    joined = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    other = models.ForeignKey("Other", on_delete=models.CASCADE, null=True, blank=True)
    # more_others = models.ManyToManyField("Other", blank=True)

    avatar = models.ImageField()

    class Meta:
        app_label = 'test_models_create'


class Other(models.Model):
    id = models.UUIDField(primary_key=True)
    name = models.CharField(max_length=255)

    class Meta:
        app_label = 'test_models_create'


def test_model_create():
    SomethingInPydantic = django_to_pydantic_model(Something)

    assert list(SomethingInPydantic.model_fields.keys()) == Contains(
        "id",
        "name",
        "age",
        "size",
        "weight",
        "birth",
        "joined",
        "email",
        "other_id",
        "avatar",
    )

    assert SomethingInPydantic.model_fields["id"].annotation == int
    assert SomethingInPydantic.model_fields["name"].annotation == str
    assert SomethingInPydantic.model_fields["age"].annotation == int | None
    assert SomethingInPydantic.model_fields["size"].annotation == float | None
    assert SomethingInPydantic.model_fields["weight"].annotation == decimal.Decimal | None
    assert SomethingInPydantic.model_fields["birth"].annotation == datetime.date | None
    assert SomethingInPydantic.model_fields["joined"].annotation == datetime.datetime | None
    if HAS_EMAIL_VALIDATOR:
        assert SomethingInPydantic.model_fields["email"].annotation == pydantic.EmailStr | None
    else:
        assert SomethingInPydantic.model_fields["email"].annotation == str | None
    assert SomethingInPydantic.model_fields["other_id"].annotation == uuid.UUID | None
    assert SomethingInPydantic.model_fields["avatar"].annotation == str


def test_model_create_include():
    assert (
        set(django_to_pydantic_model(Something, include={"id"}).__fields__.keys())
        == {"id"}
    )
    assert (
        set(django_to_pydantic_model(Something, include={"id", "name"}).__fields__.keys())
        == {"id", "name"}
    )


def test_model_create_exclude():
    assert not (
        set(django_to_pydantic_model(Something, exclude={"id"}).__fields__.keys())
        & {"id"}
    )
    assert not (
        set(django_to_pydantic_model(Something, exclude={"id", "name"}).__fields__.keys())
        & {"id", "name"}
    )
