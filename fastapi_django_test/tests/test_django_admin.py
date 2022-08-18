import pytest
from httpx import AsyncClient

from ..main import app


@pytest.mark.anyio
async def test_django_admin_exists():
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/admin/")
    assert response.status_code == 302
    assert "location" in response.headers
    assert "admin" in response.headers.get("location")
