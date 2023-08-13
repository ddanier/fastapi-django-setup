import pytest
from django.test import TestCase

from fastapi_django_test.something.models import Something


class SomethingTestCase(TestCase):
    def test_something_str(self):
        assert str(Something(name="A")) == "A"
        assert str(Something(name="B")) == "B"


class SomethingDBTestCase(TestCase):
    def setUp(self):
        Something.objects.create(name="A")
        Something.objects.create(name="B")

    def test_get_somethings(self):
        Something.objects.get(name="A")
        Something.objects.get(name="B")


# SAME AS ABOVE, but using async

pytestmark = pytest.mark.django_db(transaction=True)


def test_str():
    assert str(Something(name="A")) == "A"
    assert str(Something(name="B")) == "B"


@pytest.fixture()
async def setup_db():
    await Something.objects.acreate(name="A")
    await Something.objects.acreate(name="B")


@pytest.mark.anyio()
@pytest.mark.usefixtures("setup_db")
async def test_get_somethings():
    await Something.objects.aget(name="A")
    await Something.objects.aget(name="B")


@pytest.mark.anyio()
@pytest.mark.usefixtures("setup_db")
async def test_get_somethings_2():
    await Something.objects.aget(name="A")
    await Something.objects.aget(name="B")
