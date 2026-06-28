from aiogram import Bot, Dispatcher

from app.bot.handlers.common import router as common_router
from app.bot.handlers.documents import router as document_router
from app.core.config import settings

bot = Bot(token=settings.bot_token)
dispatcher = Dispatcher()


dispatcher.include_router(document_router)
dispatcher.include_router(common_router)