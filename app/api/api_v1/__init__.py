from fastapi import APIRouter

from core import settings
from .days_info import router as days_info_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(router=days_info_router)
