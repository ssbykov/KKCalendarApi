from fastapi import APIRouter

from .days_info import days_info_router

router = APIRouter()
router.include_router(router=days_info_router, prefix="/days")
