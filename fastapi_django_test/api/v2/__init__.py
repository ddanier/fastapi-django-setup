from fastapi import FastAPI

from fastapi_django_test import settings
from fastapi_django_test.utils.api.route_names import use_route_names_as_operation_ids

# This is just an empty example to show how to have different API versions setup
api_v2 = FastAPI(
    swagger_ui_parameters={
        "persistAuthorization": settings.DEBUG,
        "filter": True,
        "displayOperationId": True,
        "docExpansion": "none",
        "defaultModelsExpandDepth": 0,
        "displayRequestDuration": settings.DEBUG,
    },
)

use_route_names_as_operation_ids(api_v2)
