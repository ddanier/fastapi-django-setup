from types import EllipsisType
from typing import Any, Generic, Self, cast, overload

import pydantic

from .dict import model_to_dict
from .fields import FIELD_TYPE_MAP
from .types import DjangoModelT


class DjangoModelBase(pydantic.BaseModel, Generic[DjangoModelT]):
    @classmethod
    def _get_django_data(
        cls,
        obj: DjangoModelT,
    ) -> dict[str, Any]:
        return model_to_dict(obj)

    @overload
    @classmethod
    def from_django(cls, obj: None) -> None: ...

    @overload
    @classmethod
    def from_django(cls: type[Self], obj: DjangoModelT) -> Self: ...

    @classmethod
    def from_django(
        cls: type[Self],
        obj: DjangoModelT | None,
    ) -> Self | None:
        if obj is None:
            return None

        return cls.model_validate(cls._get_django_data(obj))


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
        pydantic_default: EllipsisType | None = ...
        # django field's attributes `null` and `blank` are used to determine whether it will
        # be optional in the pydantic model too
        if hasattr(field, "null") and field.null:
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
                title=str(getattr(field, "verbose_name", field.name)),
                description=str(getattr(field, "help_text", "")),
                **pydantic_params,
            ),
        )

    pydantic_model_class = cast(
        type[DjangoModelBase[DjangoModelT]],
        pydantic.create_model(  # type: ignore
            model_class.__name__,
            __base__=DjangoModelBase[model_class],  # type: ignore
            **pydantic_fields,
        ),
    )

    pydantic_model_class.__doc__ = model_class.__doc__

    return pydantic_model_class
