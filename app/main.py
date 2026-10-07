from __future__ import annotations

from functools import lru_cache

from fastapi import FastAPI, HTTPException
from pydantic import BaseModel, Field

from app.assistant import AssistantResult, StudyAssistant
from app.config import get_settings
from app.llm_client import LLMClient

app = FastAPI(title="Study Assistant")


class TurnRequest(BaseModel):
    session_id: str = Field(min_length=1, max_length=100)
    request: str = Field(min_length=1, max_length=8000)


class TurnResponse(BaseModel):
    status: str
    text: str
    sources: list[str]


@lru_cache
def get_assistant() -> StudyAssistant:
    return StudyAssistant(LLMClient(get_settings()))


def _respond(action: str, body: TurnRequest) -> TurnResponse:
    try:
        result: AssistantResult = get_assistant().handle(body.session_id, action, body.request)
        return TurnResponse(status=result.status, text=result.text, sources=result.sources)
    except RuntimeError as exc:
        raise HTTPException(status_code=503, detail=str(exc)) from exc


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/ask", response_model=TurnResponse)
def ask(body: TurnRequest) -> TurnResponse:
    return _respond("answer", body)


@app.post("/draft", response_model=TurnResponse)
def draft(body: TurnRequest) -> TurnResponse:
    return _respond("draft", body)
