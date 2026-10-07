def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context_text = "\n".join(
        f"Chunk {i + 1}:\n{chunk['text']}" for i, chunk in enumerate(context_chunks)
    )
    prompt = (
        f"Use the following context to answer the question.\n\n"
        f"Context:\n{context_text}\n\n"
        f"Question: {question}\n\n"
        f"Answer:"
    )
    return prompt


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    prompt = build_prompt(question, context_chunks)
    return prompt
