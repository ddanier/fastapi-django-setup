import pytest
from dirty_equals import IsPartialDict
from httpx import AsyncClient

from ..main import app


@pytest.mark.anyio()
async def test_hello_world():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/hello-world")
    assert response.status_code == 200
    assert response.json() == IsPartialDict(message="Hello World")
