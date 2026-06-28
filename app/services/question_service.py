from sqlalchemy.ext.asyncio import AsyncSession

from app.rag.llm import LLMServiceUnavailableError, generate_answer
from app.rag.prompt import build_rag_prompt
from app.rag.retriever import RetrievedChunk, retrieve_relevant_chunks

def build_sources(chunks: list[RetrievedChunk]) -> str:
    seen: set[str] = set()
    sources: list[str] = []

    for chunk in chunks:
        if chunk.document_name in seen:
            continue

        seen.add(chunk.document_name)
        sources.append(chunk.document_name)

    return "\n".join(f"- {source}" for source in sources)

async def build_retrieval_answer(
    session: AsyncSession,
    question: str,
) -> str:
    chunks = await retrieve_relevant_chunks(
        session=session,
        query=question,
    )

    if not chunks:
        return (
            "Я пока не нашёл подходящих фрагментов в базе знаний. "
            "Возможно, документы ещё не загружены."
        )

    parts: list[str] = [
        "Нашёл релевантные фрагменты в базе знаний:\n"
    ]

    for index, chunk in enumerate(chunks, start=1):
        preview = chunk.content[:700]

        parts.append(
            f"{index}. Источник: {chunk.document_name}, "
            f"chunk #{chunk.chunk_index}, distance={chunk.distance:.4f}\n"
            f"{preview}"
        )

    return "\n\n".join(parts)

async def build_rag_answer(
    session: AsyncSession,
    question: str,
) -> str:
    chunks = await retrieve_relevant_chunks(
        session=session,
        query=question,
    )

    if not chunks:
        return (
            "Я пока не нашёл подходящих фрагментов в базе знаний. "
            "Возможно, документы ещё не загружены."
        )

    prompt = build_rag_prompt(
        question=question,
        chunks=chunks,
    )

    try:
        answer = await generate_answer(prompt)
    except LLMServiceUnavailableError as err:
        original_exc = err.__cause__
        return (
            "Извините, ИИ-сервис временно недоступен. "
            "Попробуйте позже.\n"
            f"Пользовательская ошибка: {err}\n"
            f"Оригинальная причина (HTTP Status): {original_exc.response.status_code}\n"
            f"URL запроса: {original_exc.request.url}\n"
            f"Ответ сервера: {original_exc.response.text}"
        )

    if not answer:
        return (
            "ИИ-сервис вернул пустой ответ. "
            "Попробуйте переформулировать вопрос."
        )

    sources = build_sources(chunks)

    # print(prompt) # для теста - возвращает полностью контекст и вопрос пользователя
    return f"{answer}\n\nИсточники:\n{sources}"