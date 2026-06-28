from pathlib import Path
import shutil

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings

async def clear_database(session: AsyncSession) -> None:
    await session.execute(
        text(
            "TRUNCATE TABLE document_chunks, documents, users "
            "RESTART IDENTITY CASCADE"
        )
    )
    await session.commit()
    
def clear_uploads() -> int:
    upload_dir = Path(settings.upload_dir)
    
    if not upload_dir.exists():
        return 0
    
    delete_count = 0
    
    for path in upload_dir.iterdir():
        if path.is_file():
            path.unlink()
            delete_count += 1
        elif path.is_dir():
            shutil.rmtree(path)
            delete_count += 1
    
    return delete_count