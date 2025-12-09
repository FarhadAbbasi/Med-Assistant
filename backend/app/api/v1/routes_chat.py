from __future__ import annotations

import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.chat import ChatRequest, ChatResponse, ChatMessage, ChatHistoryResponse
from app.services.llm_client import LLMClient
from app.core.admin_settings import load_admin_settings
from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db.session import get_db
from app.db import models


router = APIRouter()


@router.post("/chat", response_model=ChatResponse)
async def chat(
    payload: ChatRequest,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatResponse:
    client = LLMClient()
    settings = load_admin_settings()
    system_prompt = settings["system_prompt"]

    # attach system prompt at the front
    messages = [{"role": "system", "content": system_prompt}] + [m.model_dump() for m in payload.messages]

    # find latest case for this user to associate chat with
    case = (
        db.query(models.Case)
        .filter(
            models.Case.tenant_id == current_user.tenant_id,
            models.Case.created_by_user_id == current_user.id,
        )
        .order_by(models.Case.created_at.desc())
        .first()
    )

    started = time.monotonic()
    content = await client._chat(messages)
    latency_ms = int((time.monotonic() - started) * 1000)

    # persist interaction if we have a case to attach to
    if case is not None:
        cfg = get_settings()
        interaction = models.Interaction(
            case_id=case.id,
            tenant_id=current_user.tenant_id,
            user_id=current_user.id,
            request_payload={
                "kind": "chat",
                "messages": [m.model_dump() for m in payload.messages],
            },
            response_payload={"assistant": content},
            llm_model=cfg.vllm_model,
            latency_ms=latency_ms,
        )
        db.add(interaction)
        db.commit()

    return ChatResponse(message=ChatMessage(role="assistant", content=content))


@router.get("/chat/history", response_model=ChatHistoryResponse)
async def chat_history(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
) -> ChatHistoryResponse:
    """Return reconstructed chat history for the latest case of the current user."""
    case = (
        db.query(models.Case)
        .filter(
            models.Case.tenant_id == current_user.tenant_id,
            models.Case.created_by_user_id == current_user.id,
        )
        .order_by(models.Case.created_at.desc())
        .first()
    )
    if case is None:
        return ChatHistoryResponse(messages=[])

    interactions = (
        db.query(models.Interaction)
        .filter(
            models.Interaction.tenant_id == current_user.tenant_id,
            models.Interaction.user_id == current_user.id,
            models.Interaction.case_id == case.id,
        )
        .order_by(models.Interaction.created_at.asc())
        .all()
    )

    messages: list[ChatMessage] = []

    for it in interactions:
        req = it.request_payload or {}
        kind = req.get("kind")
        if kind == "chat":
            # flatten stored chat turn
            for m in req.get("messages", []):
                role = m.get("role")
                content = m.get("content")
                if role in {"user", "assistant"} and content:
                    messages.append(ChatMessage(role=role, content=content))
            assistant_text = (it.response_payload or {}).get("assistant")
            if assistant_text:
                messages.append(ChatMessage(role="assistant", content=assistant_text))
        else:
            # treat as initial case analysis if we can
            if "patient_age" in req and "sex" in req and "symptoms" in req:
                age = req.get("patient_age")
                sex = req.get("sex")
                symptoms = req.get("symptoms") or []
                if isinstance(symptoms, list):
                    symptoms_str = ", ".join(map(str, symptoms))
                else:
                    symptoms_str = str(symptoms)
                user_summary = f"Analyze case: {age}y {sex}, symptoms: {symptoms_str}"
                messages.append(ChatMessage(role="user", content=user_summary))

            summary = (it.response_payload or {}).get("summary")
            if summary:
                messages.append(ChatMessage(role="assistant", content=summary))

    return ChatHistoryResponse(messages=messages)
