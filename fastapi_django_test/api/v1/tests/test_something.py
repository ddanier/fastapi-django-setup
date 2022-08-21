import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, Contains, IsAnyStr

from ....main import app
from ....something.models import Something


@pytest.fixture
@pytest.mark.django_db
@pytest.mark.usefixtures('django_db_setup')
def create_somethings():
    print("Creating somethings")
    Something.objects.create(
        name='Something 1',
    )


@pytest.mark.anyio
@pytest.mark.django_db
@pytest.mark.usefixtures('create_somethings')
async def test_hello_world(django_db_blocker):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/somethings/")
    assert response.status_code == 200
    assert response.json() == Contains(
        IsPartialDict(id=IsAnyStr),
    )
