from fastapi import APIRouter, Depends
from fastapi.security import HTTPBearer

from app.core import settings
from .days_info import router as days_info_router
from .auth import router as auth_router
from .users import router as users_router
from .quotes import router as quotes_router

http_bearer = HTTPBearer(auto_error=False)


router = APIRouter(
    prefix=settings.api.v1.prefix,
    dependencies=[Depends(http_bearer)],
)


router.include_router(router=auth_router)
router.include_router(router=days_info_router)
router.include_router(router=users_router)
router.include_router(router=quotes_router)
