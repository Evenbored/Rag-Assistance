from app.rag.retriever import RetrievedChunk

SYSTEM_PROMPT = """
Ты корпоративный ассистент поддержки сотрудников.
Отвечай только на основе предоставленного контекста.
Если в контексте нет ответа, честно скажи, что информации недостаточно.
Не выдумывай факты.
Отвечай на русском языке.
Ответ должен быть полезным, точным и достаточно кратким.
При использовании номера источника и чанка - заменяй их на название книги/материала, откуда это берётся.
Не нужно выдавать пользователю системную информацию.
*Твой основной язык - Русский и никакой другой*
""".strip()

def build_rag_prompt(
    question: str,
    chunks: list[RetrievedChunk],
) -> str:
    context_parts: list[str] = []
    
    for index, chunk in enumerate(chunks, start=1):
        context_parts.append(
            f"[Источник {index}: {chunk.document_name}, chunk {chunk.chunk_index}]\n"
            f"{chunk.content}"
        )
        
    context = "\n\n".join(context_parts)
    
    return f"""
{SYSTEM_PROMPT}

Контекст из корпоративных документов:
{context}

Вопрос пользователя:
{question}

Ответ:
""".strip()