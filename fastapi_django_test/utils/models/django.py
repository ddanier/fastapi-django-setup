import datetime
import decimal
from typing import (
    Any, Callable, Dict, Generic, List, Optional, Tuple, Type,
    TypeVar, Union, cast,
)
from uuid import UUID

import pydantic
from django.db import models
from django.forms.models import model_to_dict

SelfModelT = TypeVar("SelfModelT", bound=pydantic.BaseModel)
DjangoModelT = TypeVar("DjangoModelT", bound=models.Model)


class DjangoModelBase(pydantic.BaseModel, Generic[DjangoModelT]):
    @classmethod
    def from_django(
        cls: Type[SelfModelT],
        obj: DjangoModelT,
    ) -> SelfModelT:
        return cls.parse_obj(model_to_dict(obj))


FIELD_TYPE_MAP: Dict[
    Type[models.Field],
    Optional[Tuple[Type, Optional[Callable[[models.Field], Dict[str, Any]]]]],
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
    models.TextField: (str, lambda f: {'max_length': f.max_length}),
    models.BinaryField: (bytes, None),
    models.BooleanField: (bool, None),
    models.DateField: (datetime.date, None),
    models.DateTimeField: (datetime.datetime, None),
    models.TimeField: (datetime.time, None),
    models.DurationField: (datetime.timedelta, None),
    models.DecimalField: (decimal.Decimal, None),
    models.EmailField: (pydantic.EmailStr, None),
    # TODO: What fits best here? models.FileField: (pydantic.FilePath, None),
    # TODO: What fits best here? models.FilePathField: (pydantic.FilePath, None),
    # TODO: What fits best here? models.ImageField: (pydantic.FilePath, None),
    models.GenericIPAddressField: (pydantic.IPvAnyAddress, None),
    models.JSONField: (Union[Dict[str, Any], List], None),
    models.SlugField: (str, None),
    models.URLField: (pydantic.AnyUrl, None),
    models.UUIDField: (UUID, None),
    models.ForeignKey: (int, None),  # This might be tricky for more complex cases of IDs
    models.OneToOneField: (int, None),  # This might be tricky for more complex cases of IDs
    models.ManyToManyField: None,  # skip
}


def django_to_pydantic_model(
    model_class: Type[DjangoModelT],
) -> Type[DjangoModelBase[DjangoModelT]]:
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
            for django_field_type, pydantic_type_ in FIELD_TYPE_MAP.items():
                if isinstance(field, django_field_type):
                    pydantic_type = pydantic_type_
                    break

        if pydantic_type is None:
            raise ValueError(f"Cannot determine type of field {field.name} for "
                             f"model {model_class.__name__}")

        pydantic_default = ...
        if field.null:
            pydantic_type = Optional[pydantic_type]
            if field.blank:
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

    return cast(
        Type[DjangoModelBase[DjangoModelT]],
        pydantic.create_model(
            model_class.__name__,
            __base__=DjangoModelBase,
            **pydantic_fields,
        ),
    )
