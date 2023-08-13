import pytest
from dirty_equals import Contains, IsPartialDict, IsPositiveInt
from httpx import AsyncClient

from fastapi_django_test.something.models import Something

# Mark all tests to use the Django DB:
# Note: You could also use `pytest.mark.django_db()` as a decorator, but here all tests
# need the DB, so this is way easier.
pytestmark = pytest.mark.django_db()


@pytest.fixture()
def app():
    # Always import the app inside fixtures, so setup of the app is only done if
    # requested by the selected tests - this may reduce the time testing single files
    # by A LOT.
    from .. import api_v1

    return api_v1


@pytest.fixture()
async def create_somethings():
    await Something.objects.acreate(
        name='Something 1',
    )


@pytest.mark.anyio()
@pytest.mark.usefixtures('create_somethings', 'transactional_db')
async def test_hello_world(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/somethings/")

    assert response.status_code == 200
    assert response.json() == Contains(
        IsPartialDict(id=IsPositiveInt),
    )
