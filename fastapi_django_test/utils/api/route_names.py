from fastapi import FastAPI
from fastapi.routing import APIRoute

from ..namings import to_lower_camel


def use_route_names_as_operation_ids(application: FastAPI) -> None:
    """
    Simplify operation IDs to simplify function names of generated API clients.

    Should be called only after all routes have been added.
    """

    for route in application.routes:
        if isinstance(route, APIRoute):
            route.operation_id = to_lower_camel(route.name)
