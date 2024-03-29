from fastapi import FastAPI

from fastapi_django_test import settings
from fastapi_django_test.utils.api.route_names import use_route_names_as_operation_ids

from .endpoints.something import router as something_router

api_v1 = FastAPI(
    swagger_ui_parameters={
        "persistAuthorization": settings.DEBUG,
        "filter": True,
        "displayOperationId": True,
        "docExpansion": "none",
        "defaultModelsExpandDepth": 0,
        "displayRequestDuration": settings.DEBUG,
    },
)

api_v1.include_router(something_router)

use_route_names_as_operation_ids(api_v1)
