from fastapi import APIRouter
from app.schemas.document import DocumentIngestRequest, DocumentIngestResponse

router = APIRouter()

@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(payload: DocumentIngestRequest):
    return {"status": "accepted", "document_id": "doc_001"}
