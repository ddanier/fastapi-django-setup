import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient


@pytest.fixture()
def app():
    # Always import the app inside fixtures, so setup of the app is only done if
    # requested by the selected tests - this may reduce the time testing single files
    # by A LOT.
    from ..main import app

    return app


@pytest.mark.anyio()
async def test_hello_world(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/hello-world")
    assert response.status_code == 200
    assert response.json() == IsPartialDict(message="Hello World")


@pytest.mark.anyio()
async def test_health(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/health")
    assert response.status_code == 200
    assert response.json() == IsPartialDict(all="ok")
