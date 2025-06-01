from fastapi import APIRouter

from app.core import settings
from .views import router as days_info_router

router = APIRouter(
    tags=["Days info"],
)
router.include_router(
    days_info_router,
    prefix=settings.api.v1.days,
)
