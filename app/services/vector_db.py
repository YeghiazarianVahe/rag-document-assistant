import chromadb

from app.services.retrieval import embed_chunks, embed_query

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="documents", metadata={"hnsw:space": "cosine"}
)


def add_chunks(chunks: list[str], filename: str, doc_id: str) -> None:
    ids = []
    documents = []
    metadatas = []
    for i, chunk in enumerate(chunks):
        ids.append(f"{doc_id}_{i}")
        documents.append(chunk)
        metadatas.append(
            {
                "document_id": doc_id,
                "filename": filename,
                "chunk_index": i,
            }
        )
    embeddings = embed_chunks(chunks)
    collection.add(
        ids=ids,
        documents=documents,
        metadatas=metadatas,
        embeddings=embeddings.tolist(),
    )


def search_chunks(query: str, top_k: int = 3, max_distance: float = 0.85) -> list[dict]:
    query_embedding = embed_query(query)
    results = collection.query(
        query_embeddings=[query_embedding.tolist()],
        n_results=top_k,
    )
    documents = results.get("documents")
    distances = results.get("distances")
    metadatas = results.get("metadatas")

    if not documents or not distances or not metadatas:
        return []

    return [
        {
            "text": doc,
            "distance": float(distance),
            "metadata": metadata,
        }
        for doc, distance, metadata in zip(
            documents[0],
            distances[0],
            metadatas[0],
        )
        if distance <= max_distance
    ]


def library() -> list[dict]:
    results = collection.get(include=["metadatas"])
    metadatas = results.get("metadatas")

    if not metadatas:
        return []

    documents = {}

    for metadata in metadatas:
        if not metadata:
            continue

        doc_id = metadata.get("document_id")
        filename = metadata.get("filename")

        if doc_id and filename:
            documents[doc_id] = {
                "document_id": doc_id,
                "filename": filename,
            }

    return list(documents.values())


def document_exists(document_id: str) -> bool:
    result = collection.get(where={"document_id": document_id})
    return bool(result["ids"])


def delete_document(document_id: str) -> None:
    if not document_exists(document_id):
        return

    collection.delete(where={"document_id": document_id})
