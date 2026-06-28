

import asyncio

from aiogram import F, Router
from aiogram.types import Message
from app.bot.filters.admin import AdminFilter
from app.documents.parser import extract_text
from app.rag.splitter import split_text
from app.services.document_service import save_document_with_chunks
from app.services.file_storage import is_allowed_document, save_telegram_document
from aiogram import Bot
from app.db.session import async_session_factory
from app.rag.embeddings import embed_texts
router = Router(name="Documents")

@router.message(AdminFilter(), F.document)
async def admin_document_handler(message: Message, bot: Bot):
    document = message.document
    
    if document is None:
        return
    
    if not is_allowed_document(document.file_name):
        await message.answer(
            "Неподдерживаемый формат документа\n"
            "Поддерживается только: .txt, .pdf, .docx"
        )
        return
    
    saved_path = await save_telegram_document(bot=bot, document=document)
    
    text = await asyncio.to_thread(extract_text, saved_path)
    
    if not text.strip():
        await message.answer(
            "Документ сохранен, но текст извлечь не удалось."
            "Возможно это пустой файл."
        )
        return
    
    chunks = split_text(text)
    
    await message.answer(
        f"Документ разбит на {len(chunks)} чанков. Начинаю векторизацию..."
    )
    
    embeddings = await embed_texts(chunks)
    
    try:
        async with async_session_factory() as session:
            saved_document = await save_document_with_chunks(
                session=session,
                telegram_user=message.from_user,
                original_filename=document.file_name or "unknown",
                stored_path=saved_path,
                chunks=chunks,
                embeddings=embeddings
            )
    except ValueError:
        await message.answer(
            "Такой документ уже был загружен ранее."
            "Повторная индексация не выполнена"
        )
        return
    
    
    await message.answer(
        f"Документ сохранён в базе.\n"
        f"ID документа: {saved_document.id}\n"
        f"Имя файла: {document.file_name}\n"
        f"Размер текста: {len(text)} символов\n"
        f"Количество чанков: {len(chunks)}\n"
        f"Embeddings: сохранены"
    )

@router.message(F.document)
async def document_handler(message: Message):
    await message.answer("Загружать документы могут только администраторы")