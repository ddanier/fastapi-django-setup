from typing import List

from fastapi import APIRouter

from fastapi_django_test.something.dto import SomethingDTO
from fastapi_django_test.something.models import Something

router = APIRouter()


@router.get("/somethings/", response_model=List[SomethingDTO])
async def get_somethings() -> List[SomethingDTO]:
    return [
        SomethingDTO.from_django(something)
        async for something
        in Something.objects.all()
    ]
