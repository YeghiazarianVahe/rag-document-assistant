from io import BytesIO
from fastapi import UploadFile
from pypdf import PdfReader


def load_pdf(file: UploadFile) -> str:
    if file.content_type != "application/pdf":
        raise ValueError("Only PDF files are supported.")
    content = file.file.read()
    reader = PdfReader(BytesIO(content))
    text = ""
    for page in reader.pages:
        text += (page.extract_text() or "") + "\n"
    return text


def chunk_text(text: str, chunk_size: int = 500, overlap: int = 100) -> list[str]:
    if chunk_size <= 0:
        raise ValueError("Chunk size must be greater than 0.")
    if overlap < 0:
        raise ValueError("Overlap must be non-negative.")
    if overlap >= chunk_size:
        raise ValueError("Overlap must be less than chunk size.")
    chunks = []
    step = chunk_size - overlap
    for i in range(0, len(text), step):
        chunks.append(text[i : i + chunk_size])
    return chunks
