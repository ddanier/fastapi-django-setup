from django.db import models

class Something(models.Model):
    name = models.CharField(max_length=255)
