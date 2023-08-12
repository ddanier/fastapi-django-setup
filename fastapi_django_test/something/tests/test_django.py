from django.test import TestCase

from fastapi_django_test.something.models import Something


class SomethingTestCase(TestCase):
    def setUp(self):
        Something.objects.create(name="A")
        Something.objects.create(name="B")

    def test_get_somethings(self):
        Something.objects.get(name="A")
        Something.objects.get(name="B")
