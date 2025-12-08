from uuid import uuid4

from fastapi import APIRouter

from app.schemas.document import DocumentIngestRequest, DocumentIngestResponse
from app.core.config import get_settings
from app.services.embeddings import embed_texts
from app.services.qdrant_client import upsert_text_points


router = APIRouter()


def _split_into_chunks(text: str, max_len: int = 512) -> list[str]:
    paragraphs = [p.strip() for p in text.split("\n") if p.strip()]
    chunks: list[str] = []
    for p in paragraphs:
        while len(p) > max_len:
            chunks.append(p[:max_len])
            p = p[max_len:]
        if p:
            chunks.append(p)
    if not chunks and text.strip():
        chunks = [text.strip()]
    return chunks


@router.post("/ingest", response_model=DocumentIngestResponse)
async def ingest_document(payload: DocumentIngestRequest):
    s = get_settings()
    tenant_id = s.default_tenant_id
    chunks = _split_into_chunks(payload.content)
    vectors = await embed_texts(chunks)
    upsert_text_points(
        collection=s.qdrant_collection,
        vectors=vectors,
        texts=chunks,
        tenant_id=tenant_id,
        title=payload.title,
        source=payload.source,
    )
    document_id = str(uuid4())
    return {"status": "ingested", "document_id": document_id}
