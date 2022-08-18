import pytest
from httpx import AsyncClient
from dirty_equals import IsPartialDict, Contains, IsAnyStr

from ....main import app


@pytest.mark.anyio
async def test_hello_world():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/api/v1/somethings/")
    assert response.status_code == 200
    assert response.json() == Contains(
        IsPartialDict(id=IsAnyStr),
    )
