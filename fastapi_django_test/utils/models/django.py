from typing import Generic, Optional, Type, TypeVar, cast

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


FIELD_TYPE_MAP = {
    models.AutoField: int,
    models.SmallAutoField: int,
    models.BigAutoField: int,
    models.CharField: str,
    models.IntegerField: int,
    models.TextField: str,
    # TODO: Continue...
}


def django_to_pydantic_model(
    model_class: Type[DjangoModelT],
) -> Type[DjangoModelBase[DjangoModelT]]:
    pydantic_fields = {}

    for field in model_class._meta.get_fields(include_hidden=False):
        pydantic_type = None
        if field.__class__ in FIELD_TYPE_MAP:
            pydantic_type = FIELD_TYPE_MAP[field.__class__]

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
            pydantic_default = None

        # TODO: Handle mac_length etc. ;-)
        pydantic_fields[field.name] = (
            pydantic_type,
            pydantic.Field(
                pydantic_default,
                title=str(field.verbose_name),
                description=str(field.help_text),
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
