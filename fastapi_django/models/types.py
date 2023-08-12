from typing import TypeVar

from django.db import models

DjangoModelT = TypeVar("DjangoModelT", bound=models.Model)
