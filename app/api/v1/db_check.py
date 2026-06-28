from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.session import get_async_session


router = APIRouter(tags=["Database"])

@router.get("/db/check")
async def check_db_health(session: AsyncSession = Depends(get_async_session)) -> dict[str, str]:
    result = await session.execute(text("SELECT 1"))
    value = result.scalar_one()
    
    return {"database": "ok", "result": str(value)}