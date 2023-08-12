from typing import Any

from django.conf import settings
from django.contrib.staticfiles.handlers import ASGIStaticFilesHandler
from fastapi import FastAPI


def get_fastapi_app() -> FastAPI:
    """Return FastAPI app including the API and Django endpoints as mounts."""

    from .api.v1 import api_v1
    from .api.v2 import api_v2
    from .asgi import application as django_app

    app = FastAPI(
        # Disable any docs, as the root FastAPI instance does is only necessary to mount
        # all the other things like the API, Django, etc.
        openapi_url=None,
        docs_url=None,
        redoc_url=None,
    )

    # You may include some generic endpoints here...
    @app.get("/hello-world")
    def hello_world() -> dict[str, Any]:
        return {"message": "Hello World"}

    # ...like a health check
    @app.get("/health")
    def health() -> dict[str, Any]:
        return {"all": "ok"}

    # Mount all API versions
    app.mount("/api/v1", api_v1)
    app.mount("/api/v2", api_v2)

    # Mount Django
    if settings.DEBUG:  # pragma: no cover
        app.mount("/", ASGIStaticFilesHandler(django_app))  # type: ignore
    else:
        app.mount("/", django_app)  # type: ignore

    return app
