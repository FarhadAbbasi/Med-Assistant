from __future__ import annotations

import asyncio
from typing import List

from sentence_transformers import SentenceTransformer


_model: SentenceTransformer | None = None


def _get_model() -> SentenceTransformer:
    global _model
    if _model is None:
        # BAAI/bge-m3 as per master plan (supports multi-lingual, good for RAG)
        _model = SentenceTransformer("BAAI/bge-m3")
    return _model


async def embed_texts(texts: list[str]) -> list[list[float]]:
    loop = asyncio.get_event_loop()

    def _encode() -> List[List[float]]:
        model = _get_model()
        emb = model.encode(texts, normalize_embeddings=True)
        return emb.tolist()

    return await loop.run_in_executor(None, _encode)
