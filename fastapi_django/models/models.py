from types import EllipsisType
from typing import Any, Generic, Self, cast, overload

import pydantic
from pydantic_core._pydantic_core import PydanticUndefined, PydanticUndefinedType

from .dict import model_to_dict
from .fields import _get_pydantic_field_options_from_django_field
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
    *,
    skip_unknown_field_types: bool = False,
) -> type[DjangoModelBase[DjangoModelT]]:
    pydantic_fields = {}

    for field in model_class._meta.get_fields(include_hidden=False):
        pydantic_field_options = _get_pydantic_field_options_from_django_field(field)

        # If we found no type, abort
        if pydantic_field_options is None:
            if skip_unknown_field_types:
                continue
            raise ValueError(
                f"Cannot determine type of field {field.name} for "
                f"model {model_class.__name__}",
            )

        # Prepare all variables we are using
        pydantic_type, pydantic_params_callback = pydantic_field_options
        pydantic_default: EllipsisType | PydanticUndefinedType | None = ...
        pydantic_params = {}
        pydantic_name = field.attname if hasattr(field, "attname") else field.name

        # Allow pydantic_type to be a callable so we determine the actual type
        # lazily (used for ForeignKeys)
        if (
            not isinstance(pydantic_type, type)
            and callable(pydantic_type)
        ):
            pydantic_type = pydantic_type(field)

        # Calculate pydantic default value determine if it should allow None values
        # django field's attributes `null` and `blank` are used to determine whether it
        # will be optional in the pydantic model
        if hasattr(field, "null") and field.null:
            # Allow None in pydantic validation
            pydantic_type = pydantic_type | None
            if hasattr(field, "blank") and field.blank:
                # None as the pydantic_default marks the field as optional in the
                # OpenAPI spec
                pydantic_default = None

        # Calculate fields default value
        if hasattr(field, "default") and field.default:
            if callable(field.default):
                pydantic_params["default_factory"] = field.default
                pydantic_default = PydanticUndefined  # Ensure we don't have two defaults
            else:
                pydantic_default = field.default

        # Prepare all other field options
        if pydantic_params_callback is not None:
            pydantic_params.update(pydantic_params_callback(field))

        # Create the actual field
        pydantic_fields[pydantic_name] = (
            pydantic_type,
            pydantic.Field(
                pydantic_default,
                alias=field.name if field.name != pydantic_name else None,
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
