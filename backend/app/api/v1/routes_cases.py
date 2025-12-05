from fastapi import APIRouter, Depends, Header
from app.schemas.case import CaseInput, CaseAnalysisResponse
from app.services.llm_client import LLMClient
from app.services.rag import retrieve_context
from app.services.safety import apply_safety_postprocess
from app.core.config import get_settings

router = APIRouter()

@router.post("/analyze", response_model=CaseAnalysisResponse)
async def analyze_case(payload: CaseInput, x_tenant_id: str | None = Header(default=None)):
    contexts = await retrieve_context(payload)
    client = LLMClient()
    result = await client.analyze_case(payload, contexts)
    result = apply_safety_postprocess(result)
    return result
