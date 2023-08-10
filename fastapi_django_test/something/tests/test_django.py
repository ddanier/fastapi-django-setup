from django.test import TestCase

from fastapi_django_test.something.models import Something


class AnimalTestCase(TestCase):
    def setUp(self):
        Something.objects.create(name="A")
        Something.objects.create(name="B")

    def test_animals_can_speak(self):
        Something.objects.get(name="A")
        Something.objects.get(name="B")
