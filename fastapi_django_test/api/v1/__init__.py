from fastapi import APIRouter

from .endpoints.something import router as something_router

router = APIRouter()
router.include_router(something_router)
