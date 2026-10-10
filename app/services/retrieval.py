from sentence_transformers import SentenceTransformer
import numpy as np

model = SentenceTransformer("all-MiniLM-L6-v2")


def cosine_similarity(a, b):
    dot_product = np.dot(a, b)
    norm_a = np.linalg.norm(a)
    norm_b = np.linalg.norm(b)
    return dot_product / (norm_a * norm_b)


def embed_chunks(chunks: list[str]):
    return model.encode(chunks)


def embed_query(query: str):
    return model.encode(query)


def retrieve_chunks(
    query: str, chunks: list[str], chunk_embeddings, top_k: int = 2
) -> list[dict]:
    query_embedding = model.encode(query)

    results = []

    for chunk, chunk_embedding in zip(chunks, chunk_embeddings):
        similarity = cosine_similarity(query_embedding, chunk_embedding)
        results.append({"text": chunk, "score": float(similarity)})

    results.sort(key=lambda x: x["score"], reverse=True)

    return results[:top_k]
