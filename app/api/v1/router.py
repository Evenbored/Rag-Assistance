from fastapi import APIRouter

from app.api.v1.health import router as health_router
from app.api.v1.telegram import router as telegram_router
from app.api.v1.db_check import router as db_check_router
api_router = APIRouter(prefix="/api/v1")

api_router.include_router(health_router)
api_router.include_router(telegram_router)
api_router.include_router(db_check_router)