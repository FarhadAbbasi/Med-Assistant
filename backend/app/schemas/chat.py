from __future__ import annotations

from typing import Literal

from pydantic import BaseModel


class ChatMessage(BaseModel):
    role: Literal["system", "user", "assistant"]
    content: str


class ChatRequest(BaseModel):
    messages: list[ChatMessage]


class ChatResponse(BaseModel):
    message: ChatMessage


class ChatHistoryResponse(BaseModel):
    messages: list[ChatMessage]
