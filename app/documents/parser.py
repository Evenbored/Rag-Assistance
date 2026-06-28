
from pathlib import Path

from pypdf import PdfReader
from docx import Document as DocxDocument

def extract_text_from_txt(file_path: Path) -> str:
    for encoding in ("utf-8", "cp1251"):
        try:
            return file_path.read_text(encoding=encoding)
        except UnicodeError:
            continue
    return file_path.read_text(encoding="utf-8", errors="ignore")

def extract_text_from_pdf(file_path: Path) -> str:
    reader = PdfReader(file_path)
    
    pages_text: list[str] = []
    
    for page in reader.pages:
        text = page.extract_text()
        if text:
            pages_text.append(text)
    
    return "\n\n".join(pages_text)


def extract_text_from_docx(file_path: Path) -> str:
    document = DocxDocument(file_path)
    
    paragraphs = [
        paragraph.text for paragraph in document.paragraphs if paragraph.text.strip()
    ]
    
    return "\n\n".join(paragraphs)


def extract_text(file_path: Path) -> str:
    suffix = file_path.suffix.lower()
    
    match suffix:
        case ".txt":
            return extract_text_from_txt(file_path)
        case ".pdf":
            return extract_text_from_pdf(file_path)
        case ".docx":
            return extract_text_from_docx(file_path)
    
    raise ValueError(f"Unsupported file type: {suffix}")