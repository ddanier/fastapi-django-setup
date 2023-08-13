import datetime
import decimal
from collections.abc import Callable
from types import UnionType
from typing import Any, TypeAlias, cast
from uuid import UUID

import pydantic
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models.fields import reverse_related
from django.db.models.fields.reverse_related import ForeignObjectRel

FieldType: TypeAlias = models.Field | ForeignObjectRel | GenericForeignKey
JSONValue: TypeAlias = bool | float | int | str | None
JSONType: TypeAlias = dict[str, JSONValue] | list[JSONValue] | JSONValue
FIELD_TYPE_MAP: dict[
    type[FieldType],  # models.Field is to strict, would not catch ManyToOneRel and others
    tuple[
        type | UnionType | Callable[[FieldType], type | UnionType],
        Callable[[FieldType], dict[str, Any]] | None,
    ] | None,
] = {
    # Normal fields
    # see https://docs.djangoproject.com/en/4.2/ref/models/fields/#field-types
    models.AutoField: (int, None),
    models.BigAutoField: (int, None),
    models.BigIntegerField: (int, None),
    models.BinaryField: (bytes, None),
    models.BooleanField: (bool, None),
    models.CharField: (str, lambda f: {'max_length': f.max_length}),  # type: ignore
    models.DateField: (datetime.date, None),
    models.DateTimeField: (datetime.datetime, None),
    models.DecimalField: (decimal.Decimal, None),
    models.DurationField: (datetime.timedelta, None),
    models.EmailField: (pydantic.EmailStr, None),
    models.FileField: (str, None),  # TODO: What fits best here?
    # TODO: What fits best here? models.FilePathField: (pydantic.FilePath, None),
    models.FloatField: (float, None),
    models.GenericIPAddressField: (pydantic.IPvAnyAddress, None),
    # TODO: What fits best here? models.ImageField: (pydantic.FilePath, None),
    models.IntegerField: (int, None),
    models.JSONField: (JSONType, None),  # type: ignore
    models.PositiveBigIntegerField: (pydantic.PositiveInt, None),
    models.PositiveIntegerField: (pydantic.PositiveInt, None),
    models.PositiveSmallIntegerField: (pydantic.PositiveInt, None),
    models.SlugField: (str, None),
    models.SmallAutoField: (int, None),
    models.SmallIntegerField: (int, None),
    models.TextField: (str, lambda f: {'max_length': f.max_length}),  # type: ignore
    models.TimeField: (datetime.time, None),
    models.URLField: (pydantic.AnyUrl, None),
    models.UUIDField: (UUID, None),

    # Relationships
    # see https://docs.djangoproject.com/en/4.2/ref/models/fields/#module-django.db.models.fields.related
    models.ForeignKey: (
        # Use type of target field
        lambda f: _get_pydantic_field_type_from_django_field(
            cast(models.ForeignKey, f).target_field,
        ),
        None,
    ),
    models.ManyToManyField: None,  # skip
    models.OneToOneField: (
        # Use type of target field
        lambda f: _get_pydantic_field_type_from_django_field(
            cast(models.ForeignKey, f).target_field,
        ),
        None,
    ),

    # GenericForeignKey
    GenericForeignKey: None,  # skip

    # Reverse fields
    # see https://github.com/django/django/blob/main/django/db/models/fields/reverse_related.py
    models.ManyToOneRel: None,  # skip
    reverse_related.ManyToManyRel: None,  # skip
}


def _get_pydantic_field_options_from_django_field(
    field: FieldType,
) -> tuple[
    type | UnionType | Callable[[FieldType], type | UnionType],
    Callable[[FieldType], dict[str, Any]] | None,
] | None:
    pydantic_type = None
    pydantic_params_callback = None

    # Easy resolving of type, search for direct usage...
    if field.__class__ in FIELD_TYPE_MAP:
        pydantic_options = FIELD_TYPE_MAP[field.__class__]
        if pydantic_options is None:
            return None  # skip field
        pydantic_type, pydantic_params_callback = pydantic_options

    # ... if this fails search by instances check
    if pydantic_type is None:
        for django_field_type, pydantic_options in FIELD_TYPE_MAP.items():
            if isinstance(field, django_field_type):
                if pydantic_options is None:
                    return None  # skip field
                pydantic_type, pydantic_params_callback = pydantic_options
                break

    # pydantic_type cannot be None now, now also make mypy happy
    assert pydantic_type is not None  # noqa: S101

    return pydantic_type, pydantic_params_callback


def _get_pydantic_field_type_from_django_field(
    field: FieldType,
) -> type | UnionType:
    pydantic_field_options = _get_pydantic_field_options_from_django_field(field)

    if pydantic_field_options is None:
        raise ValueError(f"Cannot determine type for field {field.__class__}")

    if callable(pydantic_field_options[0]):
        return pydantic_field_options[0](field)

    return pydantic_field_options[0]
