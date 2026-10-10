from pydantic import BaseModel


class AskRequest(BaseModel):
    question: str
    top_k: int = 5


class AskResponse(BaseModel):
    question: str
    top_k: int
    context: list[dict]
    answer: str
    sources: list[dict]
