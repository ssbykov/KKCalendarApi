from fastapi import APIRouter

from core import settings
from .days_info import router as router_api_v1

router = APIRouter(prefix=settings.api.prefix)

router.include_router(router=router_api_v1)
