from pathlib import Path

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from aiogram.types import User as TelegramUser
from app.core.config import settings
from app.db.models.document_chunk import DocumentChunk
from app.db.models.user import User, UserRole
from app.db.models.document import Document, DocumentStatus
from app.services.file_storage import calculate_file_sha256


async def get_or_create_user(
    session: AsyncSession, 
    telegram_user: TelegramUser
) -> User:
    result = await session.execute(select(User).where(User.telegram_id == telegram_user.id))
    user = result.scalar_one_or_none()
    
    if user is not None:
        return user
    
    role = (
        UserRole.ADMIN.value 
        if telegram_user.id in settings.admin_ids 
        else UserRole.USER.value)
    
    user = User(
        telegram_id=telegram_user.id,
        username=telegram_user.username,
        first_name=telegram_user.first_name,
        role=role)
    
    session.add(user)
    await session.flush()
    
    return user


async def document_exists_by_hash(
    session: AsyncSession,
    content_hash: str
) -> bool:
    result = await session.execute(
        select(Document.id).where(Document.content_hash == content_hash)
    )
    
    return result.scalar_one_or_none() is not None

async def save_document_with_chunks(
    session: AsyncSession,
    *,
    telegram_user: TelegramUser,
    original_filename: str,
    stored_path: Path,
    chunks: list[str],
    embeddings: list[list[float]],
) -> Document:
    if len(chunks) != len(embeddings):
        raise ValueError("Chunks and embeddings count mismatch")
    
    content_hash = calculate_file_sha256(stored_path)
    
    if await document_exists_by_hash(session=session, content_hash=content_hash):
        stored_path.unlink()
        raise ValueError("Document already exists")
    
    user = await get_or_create_user(session=session, telegram_user=telegram_user)
    
    document = Document(
        original_filename=original_filename,
        stored_path=str(stored_path),
        content_hash=content_hash,
        status=DocumentStatus.PROCESSED.value,
        uploaded_by_id=user.id
    )
    
    session.add(document)
    await session.flush()
    
    for index, chunk in enumerate(chunks):
        session.add(
            DocumentChunk(
                document_id=document.id,
                chunk_index=index,
                content=chunk,
                embedding=embeddings[index]
            )
        )
    await session.commit()
    await session.refresh(document)
    
    return document