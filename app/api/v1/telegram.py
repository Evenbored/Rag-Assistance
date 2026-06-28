from fastapi import APIRouter, HTTPException, Header, status
from typing import Annotated, Any
from aiogram.types import Update
from app.core.config import settings
from app.bot.dispatcher import bot, dispatcher

router = APIRouter(prefix="/tg",tags=["Telegram"])

@router.post("/webhook")
async def telegram_webhook(update_data: dict[str, Any], 
                           secret_token: Annotated[str | None, Header(alias="X-Telegram-Bot-Api-Secret-Token")] = None) -> dict[str, bool]:
    if secret_token != settings.telegram_webhook_secret:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid Telegram secret token",)
    update = Update.model_validate(update_data, context={"bot": bot})
    await dispatcher.feed_update(bot, update)
    
    return {"ok": True}