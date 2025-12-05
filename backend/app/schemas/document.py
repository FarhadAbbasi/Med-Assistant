from pydantic import BaseModel

class DocumentIngestRequest(BaseModel):
    title: str
    content: str
    source: str | None = None

class DocumentIngestResponse(BaseModel):
    status: str
    document_id: str
