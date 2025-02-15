from fastapi import APIRouter

from core import settings
from .views import router as days_info_router

router = APIRouter(
    prefix=settings.api.v1.prefix,
    tags=["Days info"],
)
router.include_router(
    days_info_router,
    prefix=settings.api.v1.days,
)
