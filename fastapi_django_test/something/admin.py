from django.contrib import admin

from .models import Something


@admin.register(Something)
class SomethingAdmin(admin.ModelAdmin):
    pass
