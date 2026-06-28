

from dataclasses import dataclass
from sqlalchemy import and_, select
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import DocumentChunk, Document
from app.rag.embeddings import embed_text

@dataclass(slots=True)
class RetrievedChunk:
    content: str
    document_name: str
    chunk_index: int
    distance: float
    
async def retrieve_relevant_chunks(
    session: AsyncSession,
    query: str,
    limit: int = 3
)-> list[RetrievedChunk]:
    query_embedding = await embed_text(query)
    
    distance = DocumentChunk.embedding.cosine_distance(query_embedding)
        
    # stmt = (
    #     select(
    #         DocumentChunk.content,
    #         DocumentChunk.chunk_index,
    #         Document.original_filename,
    #         distance.label("distance"),
    #     )
    #     .join(Document, Document.id == DocumentChunk.document_id)
    #     .where(DocumentChunk.embedding.is_not(None))
    #     .order_by(distance)
    #     .limit(limit)
    # )
    
    best_chunks_cte = (
    select(
        DocumentChunk.document_id.label("doc_id"),
        DocumentChunk.chunk_index.label("c_index")
    )
    .where(DocumentChunk.embedding.is_not(None))
    .order_by(distance)
    .limit(limit)
    ).cte("best_chunks")

    stmt = (
        select(
            DocumentChunk.content,
            DocumentChunk.chunk_index,
            Document.original_filename,
            DocumentChunk.document_id,
            distance.label("distance")
        )
        .distinct()
        .join(Document, Document.id == DocumentChunk.document_id)
        .join(
            best_chunks_cte, 
            DocumentChunk.document_id == best_chunks_cte.c.doc_id
        )
        .where(
            and_(
                DocumentChunk.chunk_index >= best_chunks_cte.c.c_index - 2,
                DocumentChunk.chunk_index <= best_chunks_cte.c.c_index + 2
            )
        )
        .order_by(distance)
    )
        
    result = await session.execute(stmt)
    
    return [
        RetrievedChunk(
            content=row.content,
            document_name=row.original_filename,
            chunk_index=row.chunk_index,
            distance=float(row.distance),
        )
        for row in result
    ]