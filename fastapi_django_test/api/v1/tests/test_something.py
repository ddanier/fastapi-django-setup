import pytest
from dirty_equals import Contains, IsPartialDict, IsPositiveInt
from httpx import AsyncClient

from ....main import app
from ....something.models import Something


@pytest.fixture()
@pytest.mark.django_db()
def create_somethings():  # noqa: PT004
    Something.objects.create(
        name='Something 1',
    )


@pytest.mark.anyio()
@pytest.mark.django_db()
@pytest.mark.usefixtures('create_somethings', 'transactional_db')
async def test_hello_world():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/somethings/")

    assert response.status_code == 200
    assert response.json() == Contains(
        IsPartialDict(id=IsPositiveInt),
    )
