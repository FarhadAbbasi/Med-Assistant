from typing import Iterable

from qdrant_client import QdrantClient
from qdrant_client.http import models as qmodels

from app.core.config import get_settings


_client: QdrantClient | None = None


def get_qdrant() -> QdrantClient:
    global _client
    if _client is None:
        s = get_settings()
        _client = QdrantClient(host=s.qdrant_host, port=s.qdrant_port)
        _ensure_collection(_client, s.qdrant_collection, s.embeddings_dim)
    return _client


def _ensure_collection(client: QdrantClient, collection_name: str, vector_size: int) -> None:
    existing = [c.name for c in client.get_collections().collections]
    if collection_name in existing:
        return
    client.recreate_collection(
        collection_name=collection_name,
        vectors_config=qmodels.VectorParams(size=vector_size, distance=qmodels.Distance.COSINE),
    )


def upsert_text_points(
    collection: str,
    vectors: list[list[float]],
    texts: list[str],
    tenant_id: str,
    title: str,
    source: str | None = None,
) -> None:
    client = get_qdrant()
    points: list[qmodels.PointStruct] = []
    for idx, (vec, text) in enumerate(zip(vectors, texts)):
        payload = {
            "tenant_id": tenant_id,
            "title": title,
            "source": source,
            "text": text,
        }
        points.append(
            qmodels.PointStruct(
                id=idx,
                vector=vec,
                payload=payload,
            )
        )
    if points:
        client.upsert(
            collection_name=collection,
            points=points,
        )


def search_similar_texts(
    collection: str,
    query_vector: list[float],
    tenant_id: str,
    limit: int = 5,
) -> list[str]:
    client = get_qdrant()
    results = client.search(
        collection_name=collection,
        query_vector=query_vector,
        limit=limit,
        query_filter=qmodels.Filter(
            must=[qmodels.FieldCondition(key="tenant_id", match=qmodels.MatchValue(value=tenant_id))]
        ),
    )
    texts: list[str] = []
    for r in results:
        payload = r.payload or {}
        text = payload.get("text")
        if isinstance(text, str):
            texts.append(text)
    return texts
