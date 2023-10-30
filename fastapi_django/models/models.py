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
    skip_unknown_field_types: bool = True,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
) -> type[DjangoModelBase[DjangoModelT]]:
    pydantic_fields = {}

    django_fields = model_class._meta.get_fields(include_hidden=False)
    for django_field in django_fields:
        if (
            (
                # Skip excluded fields
                exclude is not None
                and (
                    django_field.name in exclude
                    or (
                        hasattr(django_field, "attname")
                        and django_field.attname in exclude
                    )
                )
            ) or (
                # Skip fields not included
                include is not None
                and (
                    django_field.name not in include
                    or (
                        hasattr(django_field, "attname")
                        and django_field.attname not in include
                    )
                )
            )
        ):
            continue

        pydantic_field_options = _get_pydantic_field_options_from_django_field(django_field)

        # If we found no type, abort
        if pydantic_field_options is None:
            if skip_unknown_field_types:
                continue
            raise ValueError(
                f"Cannot determine type of field {django_field.name} for "
                f"model {model_class.__name__}",
            )

        # Prepare all variables we are using
        pydantic_type, pydantic_params_callback = pydantic_field_options
        pydantic_default: EllipsisType | PydanticUndefinedType | None = ...
        pydantic_params = {}
        pydantic_name = django_field.attname if hasattr(django_field, "attname") else django_field.name

        # Allow pydantic_type to be a callable so we determine the actual type
        # lazily (used for ForeignKeys)
        if (
            not isinstance(pydantic_type, type)
            and callable(pydantic_type)
        ):
            pydantic_type = pydantic_type(django_field)

        # Calculate pydantic default value determine if it should allow None values
        # django field's attributes `null` and `blank` are used to determine whether it
        # will be optional in the pydantic model
        if hasattr(django_field, "null") and django_field.null:
            # Allow None in pydantic validation
            pydantic_type = pydantic_type | None
            if hasattr(django_field, "blank") and django_field.blank:
                # None as the pydantic_default marks the field as optional in the
                # OpenAPI spec
                pydantic_default = None

        # Calculate fields default value
        if hasattr(django_field, "default") and django_field.default:
            if callable(django_field.default):
                pydantic_params["default_factory"] = django_field.default
                pydantic_default = PydanticUndefined  # Ensure we don't have two defaults
            else:
                pydantic_default = django_field.default

        # Prepare all other field options
        if pydantic_params_callback is not None:
            pydantic_params.update(pydantic_params_callback(django_field))

        # Create the actual field
        pydantic_fields[pydantic_name] = (
            pydantic_type,
            pydantic.Field(
                pydantic_default,
                alias=django_field.name if django_field.name != pydantic_name else None,
                title=str(getattr(django_field, "verbose_name", django_field.name)),
                description=str(getattr(django_field, "help_text", "")),
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
