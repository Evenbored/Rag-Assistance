

import asyncio
from functools import lru_cache
from app.core.config import settings
from sentence_transformers import SentenceTransformer


@lru_cache(maxsize=1)
def get_embedding_model() -> SentenceTransformer:
    return SentenceTransformer(settings.embedding_model_name)

def embed_text_sync(text: str) -> list[float]:
    model = get_embedding_model()
    embedding = model.encode(text, normalize_embeddings=True)
    return embedding.tolist()

async def embed_text(text: str) -> list[float]:
    return await asyncio.to_thread(embed_text_sync, text)


def embed_texts_sync(texts: list[str]) -> list[list[float]]:
    model = get_embedding_model()
    embeddings = model.encode(texts, normalize_embeddings=True, batch_size=16)
    return embeddings.tolist()

async def embed_texts(texts: list[str]) -> list[list[float]]:
    return await asyncio.to_thread(embed_texts_sync, texts)

