import datetime
import decimal
from collections.abc import Callable
from types import UnionType
from typing import Any, TypeAlias
from uuid import UUID

import pydantic
from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models.fields import reverse_related
from django.db.models.fields.reverse_related import ForeignObjectRel

FieldType: TypeAlias = models.Field | ForeignObjectRel | GenericForeignKey
FIELD_TYPE_MAP: dict[
    type[FieldType],  # models.Field is to strict, would not catch ManyToOneRel and others
    tuple[type | UnionType, Callable[[FieldType], dict[str, Any]] | None] | None,
] = {
    models.AutoField: (int, None),
    models.SmallAutoField: (int, None),
    models.BigAutoField: (int, None),
    models.CharField: (str, lambda f: {'max_length': f.max_length}),  # type: ignore
    models.IntegerField: (int, None),
    models.PositiveIntegerField: (pydantic.PositiveInt, None),
    models.SmallIntegerField: (int, None),
    models.PositiveSmallIntegerField: (pydantic.PositiveInt, None),
    models.BigIntegerField: (int, None),
    models.PositiveBigIntegerField: (pydantic.PositiveInt, None),
    models.FloatField: (float, None),
    models.TextField: (str, lambda f: {'max_length': f.max_length}),  # type: ignore
    models.BinaryField: (bytes, None),
    models.BooleanField: (bool, None),
    models.DateField: (datetime.date, None),
    models.DateTimeField: (datetime.datetime, None),
    models.TimeField: (datetime.time, None),
    models.DurationField: (datetime.timedelta, None),
    models.DecimalField: (decimal.Decimal, None),
    models.EmailField: (pydantic.EmailStr, None),
    models.FileField: (str, None),  # TODO: What fits best here?
    # TODO: What fits best here? models.FilePathField: (pydantic.FilePath, None),
    # TODO: What fits best here? models.ImageField: (pydantic.FilePath, None),
    models.GenericIPAddressField: (pydantic.IPvAnyAddress, None),
    models.JSONField: (dict[str, Any] | list[Any], None),
    models.SlugField: (str, None),
    models.URLField: (pydantic.AnyUrl, None),
    models.UUIDField: (UUID, None),
    models.ForeignKey: (int, None),  # This might be tricky for more complex cases of IDs
    models.OneToOneField: (int, None),  # This might be tricky for more complex cases of IDs
    models.ManyToManyField: None,  # skip
    models.ManyToOneRel: None,  # skip
    reverse_related.ManyToManyRel: None,  # skip
}
