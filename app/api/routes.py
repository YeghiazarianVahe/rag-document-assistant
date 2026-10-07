from fastapi import APIRouter, UploadFile, File, HTTPException
from app.models.schemas import AskRequest, AskResponse
from app.services.document import load_pdf, chunk_text
from app.services.retrieval import embed_chunks, retrieve_chunks
from app.services.llm import generate_answer

router = APIRouter()
chunks = []
chunk_embeddings = []


@router.get("/health")
def health():
    return {"status": "ok"}


@router.post("/ask", response_model=AskResponse)
def ask(request: AskRequest):
    if not chunks:
        raise HTTPException(status_code=400, detail="No document uploaded yet.")
    context = retrieve_chunks(request.question, chunks, chunk_embeddings, request.top_k)
    answer = generate_answer(request.question, context)
    return {
        "question": request.question,
        "top_k": request.top_k,
        "context": context,
        "answer": answer,
    }


@router.post("/documents")
async def upload_document(file: UploadFile = File(...)):
    global chunks, chunk_embeddings
    try:
        loaded_text = load_pdf(file)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    if not loaded_text.strip():
        raise HTTPException(status_code=400, detail="No extractable text found in PDF.")
    chunks = chunk_text(loaded_text)
    chunk_embeddings = embed_chunks(chunks)
    return {
        "filename": file.filename,
        "characters": len(loaded_text),
        "chunks": len(chunks),
    }
