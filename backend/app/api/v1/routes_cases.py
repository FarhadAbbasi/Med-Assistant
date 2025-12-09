import time

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.schemas.case import CaseInput, CaseAnalysisResponse
from app.services.llm_client import LLMClient
from app.services.rag import retrieve_context
from app.services.safety import apply_safety_postprocess
from app.core.config import get_settings
from app.core.deps import get_current_user
from app.db import models
from app.db.session import get_db

router = APIRouter()

@router.post("/analyze", response_model=CaseAnalysisResponse)
async def analyze_case(
    payload: CaseInput,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db),
):
    tenant_id = current_user.tenant_id

    case = models.Case(
        tenant_id=tenant_id,
        created_by_user_id=current_user.id,
        patient_age=payload.patient_age,
        sex=payload.sex,
        symptoms=payload.symptoms,
        history=payload.history,
        medications=payload.medications,
        vitals=payload.vitals,
    )
    db.add(case)
    db.commit()
    db.refresh(case)

    contexts = await retrieve_context(payload, tenant_id=str(tenant_id))
    client = LLMClient()

    started = time.monotonic()
    result = await client.analyze_case(payload, contexts)
    latency_ms = int((time.monotonic() - started) * 1000)

    result = apply_safety_postprocess(result)

    settings = get_settings()
    request_payload = {"kind": "analyze_case"}
    request_payload.update(payload.model_dump())

    interaction = models.Interaction(
        case_id=case.id,
        tenant_id=tenant_id,
        user_id=current_user.id,
        request_payload=request_payload,
        response_payload=result.model_dump(),
        llm_model=settings.vllm_model,
        latency_ms=latency_ms,
    )
    db.add(interaction)
    db.commit()

    return result
