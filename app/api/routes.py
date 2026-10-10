from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import AskRequest, AskResponse
from app.services.document import load_pdf, chunk_text
from app.services.vector_db import (
    add_chunks,
    search_chunks,
    library,
    delete_document,
    document_exists,
)
from app.services.llm import generate_answer
from uuid import uuid4

router = APIRouter()


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    try:
        text = load_pdf(file)
    except ValueError as e:
        raise HTTPException(
            status_code=400,
            detail=str(e),
        )

    if not text.strip():
        raise HTTPException(
            status_code=400,
            detail="No extractable text found in PDF.",
        )

    chunks = chunk_text(text)
    filename = file.filename or "uploaded_document.pdf"
    doc_id = str(uuid4())
    add_chunks(chunks, filename, doc_id)

    return {
        "document_id": doc_id,
        "filename": file.filename,
        "characters": len(text),
        "chunks": len(chunks),
    }


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    context = search_chunks(request.question, request.top_k)
    sources = [
        {
            "filename": item["metadata"]["filename"],
            "chunk_index": item["metadata"]["chunk_index"],
        }
        for item in context
    ]
    if not context:
        return {
            "question": request.question,
            "top_k": request.top_k,
            "context": [],
            "sources": [],
            "answer": "I don't know based on the provided documents.",
        }
    answer = generate_answer(request.question, context)
    return {
        "question": request.question,
        "top_k": request.top_k,
        "context": context,
        "sources": sources,
        "answer": answer,
    }


@router.get("/library")
def get_documents():
    return {"documents": library()}


@router.delete("/library/{document_id}")
def delete_document_route(document_id: str):
    if not document_exists(document_id):
        raise HTTPException(status_code=404, detail="Document not found.")

    delete_document(document_id)

    return {"status": "deleted", "document_id": document_id}
