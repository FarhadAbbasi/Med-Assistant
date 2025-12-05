from qdrant_client import QdrantClient
from app.core.config import get_settings

_client: QdrantClient | None = None

def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        s = get_settings()
        _client = QdrantClient(host=s.qdrant_host, port=s.qdrant_port)
    return _client
