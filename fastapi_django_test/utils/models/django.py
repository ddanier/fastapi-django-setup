import datetime
import decimal
from collections.abc import Callable
from typing import Any, Generic, Self, TypeVar, Union, cast, overload
from uuid import UUID

from django.db import models
from django.db.models import FileField
from django.db.models.fields import reverse_related

import pydantic

DjangoModelT = TypeVar("DjangoModelT", bound=models.Model)


def model_to_dict(
    instance: Any,
    include: list[str] = None,
    exclude: list[str] = None,
) -> dict[str, Any]:
    """
    Return a dict containing the data in ``instance``.

    Suitable for passing as a Form's ``initial`` keyword argument.

    ``fields`` is an optional list of field names. If provided, return only the
    named.

    ``exclude`` is an optional list of field names. If provided, exclude the
    named from the returned dict, even if they are listed in the ``fields``
    argument.
    """

    opts = instance._meta
    data = {}
    for field in opts.get_fields():
        if include is not None and field.name not in include:
            continue
        if exclude and field.name in exclude:
            continue
        if isinstance(field, FileField):
            # Check if a file has been set
            # Comparison to None does not work because the field still contains a FieldFile Object
            field_file = field.value_from_object(instance)
            # If the FileField is *not set*, then field_file is not None
            # (it is still a FieldFile object even if the field is blank), but it is not False in every way
            # you would expect either.
            # field_file is None: False
            # field_file is False: False
            # field_file is True: False
            # bool(field_file): False
            if field_file:
                # If field_file is True, then a file is currently attached to the FileField
                data[field.name] = field_file.url
            continue
        if isinstance(field, models.ManyToManyField):
            # Skip ManyToManyFields: need to be handled separately
            continue
        if isinstance(field, models.ManyToOneRel):
            # Skip reverse relations: need to be handled separately
            continue
        if isinstance(field, reverse_related.ManyToManyRel):
            # Skip reverse relations: need to be handled separately
            continue
        # If no special handling is needed, just call the fields value_from_object method on the instance
        data[field.name] = field.value_from_object(instance)
    return data


class DjangoModelBase(pydantic.BaseModel, Generic[DjangoModelT]):
    @classmethod
    def _get_from_django_data(
        cls: Self,
        obj: DjangoModelT,
    ) -> dict:
        return model_to_dict(obj)

    @overload
    @classmethod
    def from_django(cls: Self, obj: None) -> None: ...

    @overload
    @classmethod
    def from_django(cls: Self, obj: DjangoModelT) -> Self: ...

    @classmethod
    def from_django(
        cls: Self,
        obj: DjangoModelT | None,
    ) -> Self | None:
        if obj is None:
            return None

        return cls.parse_obj(cls._get_from_django_data(obj))


FIELD_TYPE_MAP: dict[
    type[models.Field],
    tuple[type, Callable[[models.Field], dict[str, Any]] | None] | None,
] = {
    models.AutoField: (int, None),
    models.SmallAutoField: (int, None),
    models.BigAutoField: (int, None),
    models.CharField: (str, lambda f: {'max_length': f.max_length}),
    models.IntegerField: (int, None),
    models.PositiveIntegerField: (pydantic.PositiveInt, None),
    models.SmallIntegerField: (int, None),
    models.PositiveSmallIntegerField: (pydantic.PositiveInt, None),
    models.BigIntegerField: (int, None),
    models.PositiveBigIntegerField: (pydantic.PositiveInt, None),
    models.FloatField: (float, None),
    models.TextField: (str, lambda f: {'max_length': f.max_length}),
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
    models.JSONField: (Union[dict[str, Any], list], None),
    models.SlugField: (str, None),
    models.URLField: (pydantic.AnyUrl, None),
    models.UUIDField: (UUID, None),
    models.ForeignKey: (int, None),  # This might be tricky for more complex cases of IDs
    models.OneToOneField: (int, None),  # This might be tricky for more complex cases of IDs
    models.ManyToManyField: None,  # skip
    models.ManyToOneRel: None,  # skip
    reverse_related.ManyToManyRel: None,  # skip
}


def django_to_pydantic_model(
    model_class: type[DjangoModelT],
) -> type[DjangoModelBase[DjangoModelT]]:
    pydantic_fields = {}

    for field in model_class._meta.get_fields(include_hidden=False):
        pydantic_type = None
        pydantic_params_callback = None
        if field.__class__ in FIELD_TYPE_MAP:
            pydantic_config = FIELD_TYPE_MAP[field.__class__]
            if pydantic_config is None:
                continue  # skip field
            pydantic_type, pydantic_params_callback = pydantic_config

        if pydantic_type is None:
            skip_field = False
            for django_field_type, pydantic_config in FIELD_TYPE_MAP.items():
                if isinstance(field, django_field_type):
                    if pydantic_config is None:
                        skip_field = True
                        continue  # skip loop
                    pydantic_type, pydantic_params_callback = pydantic_config
                    break
            if skip_field:
                continue  # skip field

        if pydantic_type is None:
            raise ValueError(
                f"Cannot determine type of field {field.name} for "
                f"model {model_class.__name__}",
            )

        # Ellipsis ... as the pydantic_default marks the field as required
        pydantic_default = ...
        # django field's attributes `null` and `blank` are used to determine whether it will
        # be optional in the pydantic model too
        if field.null:
            # Allow None in pydantic validation
            pydantic_type = pydantic_type | None
            if hasattr(field, "blank") and field.blank:
                # None as the pydantic_default marks the field as optional in the OpenAPI spec
                pydantic_default = None

        pydantic_params = {}
        if pydantic_params_callback is not None:
            pydantic_params = pydantic_params_callback(field)
        pydantic_fields[field.name] = (
            pydantic_type,
            pydantic.Field(
                pydantic_default,
                title=str(field.verbose_name),
                description=str(field.help_text),
                **pydantic_params,
            ),
        )

    pydantic_model_class = cast(
        type[DjangoModelBase[DjangoModelT]],
        pydantic.create_model(
            model_class.__name__,
            __base__=DjangoModelBase,
            **pydantic_fields,
        ),
    )

    pydantic_model_class.__doc__ = model_class.__doc__

    return pydantic_model_class
