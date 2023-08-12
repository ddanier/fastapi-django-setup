from typing import Any

from django.contrib.contenttypes.fields import GenericForeignKey
from django.db import models
from django.db.models import FileField


def model_to_dict(
    instance: models.Model,
    include: set[str] | None = None,
    exclude: set[str] | None = None,
) -> dict[str, Any]:
    """
    Return a dict containing the data in ``instance``.

    Suitable for passing as a Form's ``initial`` keyword argument.

    ``include`` is an optional list of field names. If provided, return only the
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
        if isinstance(field, models.ForeignObjectRel):
            # Skip reverse relations: need to be handled separately
            continue
        if isinstance(field, GenericForeignKey):
            # Skip generic foreign keys: need to be handled separately
            continue
        # If no special handling is needed, just call the fields value_from_object method on the instance
        data[field.name] = field.value_from_object(instance)
    return data
