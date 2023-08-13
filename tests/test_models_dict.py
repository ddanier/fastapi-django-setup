import datetime
import decimal

from dirty_equals import IsPartialDict
from django.core.files.storage import InMemoryStorage
from django.db import models

from fastapi_django.models import model_to_dict

storage = InMemoryStorage(
    base_url="/web/url/",
)


class Something(models.Model):
    name = models.CharField(max_length=255)
    age = models.IntegerField(null=True, blank=True)
    size = models.FloatField(null=True, blank=True)
    weight = models.DecimalField(null=True, blank=True)
    birth = models.DateField(null=True, blank=True)
    joined = models.DateTimeField(null=True, blank=True)
    email = models.EmailField(null=True, blank=True)

    main_other = models.ForeignKey("Other", on_delete=models.CASCADE, null=True, blank=True)
    others = models.ManyToManyField("Other", related_name="+")

    avatar = models.ImageField(storage=storage)

    class Meta:
        app_label = 'test'


class Other(models.Model):
    name = models.CharField(max_length=255)

    something = models.ManyToManyField(Something, related_name="reverse_others")

    class Meta:
        app_label = 'test'


def test_model_to_dict_for_simple_fields():
    something = Something(
        name="max",
        age=123,
        size=12.3,
        weight=decimal.Decimal("12.3"),
        birth=datetime.date(2023, 1, 1),
        joined=datetime.datetime(2023, 1, 1, 12, 34, 56),
        email="max@muster.de",
    )

    obj_dict = model_to_dict(something)

    assert obj_dict == IsPartialDict(
        name="max",
        age=123,
        size=12.3,
        weight=decimal.Decimal("12.3"),
        birth=datetime.date(2023, 1, 1),
        joined=datetime.datetime(2023, 1, 1, 12, 34, 56),
        email="max@muster.de",
    )


def test_model_to_dict_include():
    something = Something(
        name="max",
        age=123,
    )

    obj_dict = model_to_dict(something, include={"name"})

    assert obj_dict == IsPartialDict(name="max")
    assert obj_dict != IsPartialDict(age=123)


def test_model_to_dict_exclude():
    something = Something(
        name="max",
        age=123,
        size=12.3,
    )

    obj_dict = model_to_dict(something, exclude={"age"})

    assert obj_dict == IsPartialDict(name="max", size=12.3)
    assert obj_dict != IsPartialDict(age=123)


def test_model_to_dict_include_and_exclude():
    something = Something(
        name="max",
        age=123,
        size=12.3,
    )

    obj_dict = model_to_dict(something, include={"name", "age"}, exclude={"age"})

    assert obj_dict == IsPartialDict(name="max")
    assert obj_dict != IsPartialDict(age=123)


def test_model_to_dict_for_foreign_key():
    other = Other(id=1, name="moritz")
    something = Something(
        name="max",
        main_other=other,
    )

    obj_dict = model_to_dict(something)

    assert obj_dict == IsPartialDict(
        # Will just store the ID
        main_other=1,
    )


def test_model_to_dict_for_file_field():
    something = Something(
        name="max",
        avatar="path/to/file.jpg",
    )

    obj_dict = model_to_dict(something)

    assert obj_dict == IsPartialDict(
        avatar="/web/url/path/to/file.jpg",
    )
