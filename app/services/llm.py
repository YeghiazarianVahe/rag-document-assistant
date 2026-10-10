import os
from anthropic import Anthropic
from dotenv import load_dotenv

load_dotenv()

client = Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-haiku-5-5"


def build_prompt(question: str, context_chunks: list[dict]) -> str:
    context_text = "\n".join(
        f"Chunk {i + 1}:\n{chunk['text']}" for i, chunk in enumerate(context_chunks)
    )
    prompt = f"""
        You are a document question-answering assistant.

        Use only the provided context to answer the question.
        Reason carefully about numbers, dates, and time periods.
        You may perform simple arithmetic and time comparisons.
        For example, two weeks means 14 days.

        Do not invent information.
        If the context does not contain enough information, say:
        "I don't know based on the provided context."

        Context:
        {context_text}

        Question:
        {question}

        Answer:
    """
    return prompt.strip()


def generate_answer(question: str, context_chunks: list[dict]) -> str:
    prompt = build_prompt(question, context_chunks)
    message = client.messages.create(
        model=MODEL,
        max_tokens=256,
        messages=[
            {
                "role": "user",
                "content": prompt,
            }
        ],
    )

    for block in message.content:
        if block.type == "text":
            return block.text

    return ""
