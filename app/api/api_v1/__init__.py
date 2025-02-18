from fastapi import APIRouter

from core import settings
from .days_info import router as days_info_router
from .auth import router as auth_router

router = APIRouter(prefix=settings.api.v1.prefix)

router.include_router(router=auth_router)
router.include_router(router=days_info_router)
