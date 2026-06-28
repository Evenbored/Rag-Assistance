
from hashlib import sha256
from uuid import uuid4

from aiogram import Bot
from aiogram.types import Document
from app.core.config import settings
from pathlib import Path

def calculate_file_sha256(file_path: Path) -> str:
    hasher = sha256()
    
    with file_path.open("rb") as file:
        for chunk in iter(lambda: file.read(1024 * 1024), b""):
            hasher.update(chunk)
    
    return hasher.hexdigest()
    
def is_allowed_document(filename: str | None):
    if filename is None:
        return False
    
    suffix = Path(filename).suffix.lower()
    return suffix in settings.allowed_extensions

async def save_telegram_document(bot: Bot, document: Document) -> Path:
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    
    original_filename = document.file_name or "document.txt"
    suffix = Path(original_filename).suffix.lower()
    safe_filename = f"{uuid4().hex}{suffix}"
    
    destination = upload_dir / safe_filename
    
    file = await bot.get_file(document.file_id)
    
    await bot.download_file(file.file_path, destination)
    
    return destination