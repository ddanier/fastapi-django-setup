from fastapi import FastAPI
from fastapi.middleware.wsgi import WSGIMiddleware

from django.contrib.staticfiles.handlers import StaticFilesHandler
from django.conf import settings

from .wsgi import application as django_app
from .api.v1 import router as v1_router
from .utils.api.route_names import use_route_names_as_operation_ids

app = FastAPI(
    openapi_url="/api/v1/openapi.json",
    docs_url="/api/v1/docs",
    redoc_url="/api/v1/redoc",
    swagger_ui_parameters={
        "persistAuthorization": settings.DEBUG,
        "filter": True,
        "displayOperationId": True,
        "docExpansion": "none",
        "defaultModelsExpandDepth": 0,
        "displayRequestDuration": settings.DEBUG,
    },
)


@app.get("/hello-world", include_in_schema=False)
def read_main():
    return {"message": "Hello World"}


app.include_router(v1_router, prefix="/api/v1")
use_route_names_as_operation_ids(app)


if settings.DEBUG:
    app.mount("/", WSGIMiddleware(StaticFilesHandler(django_app)))
else:
    app.mount("/", WSGIMiddleware(django_app))
