import asyncio

from aiogram import Router
from aiogram.filters import Command, CommandStart
from aiogram.types import Message
from aiogram import F
from app.db.session import async_session_factory
from app.bot.filters.admin import AdminFilter
from app.services.maintenance import clear_database, clear_uploads
from app.services.question_service import build_rag_answer

router = Router(name="common")

@router.message(CommandStart())
async def start_handler(message: Message) -> None:
    await message.answer("Привет! Я корпоративный RAG-ассистент. "
        "Позже я смогу отвечать на вопросы по документам компании.")


@router.message(AdminFilter(), Command("clear"))
async def clear_handler(message: Message) -> None:
    async with async_session_factory() as session:
        await clear_database(session=session)

    deleted_file_count = await asyncio.to_thread(clear_uploads)
    
    await message.answer(
        "База данных и uploads очищены\n"
        f"Файлов удалено из uploads: {deleted_file_count}"
    )
    
@router.message(F.text)
async def text_message_handler(message: Message) -> None:
    if message.text is None:
        return

    await message.bot.send_chat_action(
        chat_id=message.chat.id,
        action="typing",
    )

    async with async_session_factory() as session:
        answer = await build_rag_answer(
        session=session,
        question=message.text,
    )

    await message.answer(answer)