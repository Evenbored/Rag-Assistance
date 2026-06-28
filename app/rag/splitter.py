
def split_text(text: str, chunk_size: int = 600, overlap: int = 80) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("Chunk_size must be positive")
    if overlap < 0:
        raise ValueError("Overlap cannot be negative")
    
    if overlap > chunk_size:
        raise ValueError("Overlap must be less than chunk_size")
    
    clean_text = " ".join(text.split())
    
    if not clean_text:
        return []
    
    chunks: list[str] = []
    start = 0
    
    while start < len(clean_text):
        end = start + chunk_size
        chunk = clean_text[start:end]

        chunks.append(chunk)
        
        if end >= len(clean_text):
            break
        
        start = end - overlap
    
    return chunks