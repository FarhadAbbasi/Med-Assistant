from fastapi import APIRouter
from app.schemas.note import NoteInput, NoteSummaryResponse
from app.services.llm_client import LLMClient

router = APIRouter()

@router.post("/summarize", response_model=NoteSummaryResponse)
async def summarize_notes(payload: NoteInput):
    client = LLMClient()
    return await client.summarize_notes(payload)
