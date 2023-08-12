import pytest
from httpx import AsyncClient


@pytest.fixture()
def app():
    # Always import the app inside fixtures, so setup of the app is only done if
    # requested by the selected tests - this may reduce the time testing single files
    # by A LOT.
    from ..main import app

    return app


@pytest.mark.anyio()
async def test_django_admin_exists(app):
    async with AsyncClient(app=app, base_url="http://test") as ac:
        response = await ac.get("/admin/")
    assert response.status_code == 302
    assert "location" in response.headers
    assert "admin" in response.headers.get("location")
