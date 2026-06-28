import asyncio
from collections.abc import AsyncGenerator
from contextlib import asynccontextmanager
import logging

from fastapi import FastAPI
from app.core.config import settings
from app.api.v1.router import api_router
from app.bot.dispatcher import bot
from app.rag.embeddings import get_embedding_model

logger = logging.getLogger(__name__)

@asynccontextmanager
async def lifespan(app: FastAPI) -> AsyncGenerator[None, None]:
    if settings.telegram_webhook_url:
        await bot.set_webhook(
            url=settings.telegram_webhook_url,
            secret_token=settings.telegram_webhook_secret,
            allowed_updates=["message", "callback_query"],
            drop_pending_updates=False,
        )
        logger.info("Telegram webhook has been set: %s", settings.telegram_webhook_url)
    
    if settings.warmup_embedding_model:
        logger.info("Warming up embedding model: %s", settings.embedding_model_name)
        await asyncio.to_thread(get_embedding_model)
        logger.info("Embedding model warmed up.")
    
    try:
        yield
    finally:
        if settings.delete_webhook_on_shutdown:
            await bot.delete_webhook(drop_pending_updates=False)
            logger.info("Telegram webhook has been deleted")
        
        await bot.session.close()
        logger.info("Telegram bot session has been closed.")

app = FastAPI(title=settings.app_title, version=settings.app_version, debug=settings.debug, lifespan=lifespan)
app.include_router(api_router)