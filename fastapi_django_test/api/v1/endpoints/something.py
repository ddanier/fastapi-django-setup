from typing import Annotated

from fastapi import APIRouter, Path

from fastapi_django_test.something.dto import SomethingDTO
from fastapi_django_test.something.models import Something

router = APIRouter()


# Note: You should NEVER just return a list, this is just for demo purposes, use a
#       object containing the list instead.
@router.get("/somethings/", response_model=list[SomethingDTO])
async def get_somethings() -> list[SomethingDTO]:
    return [
        SomethingDTO.from_django(something)
        async for something
        in Something.objects.all()
    ]


@router.get("/somethings/{id}/", response_model=SomethingDTO)
async def get_something_by_id(
    id_: Annotated[int, Path(..., alias="id")],
) -> list[SomethingDTO]:
    something = await Something.objects.aget(id=id_)

    return SomethingDTO.from_django(something)
