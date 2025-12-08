from app.schemas.case import CaseInput
from app.core.config import get_settings
from app.services.embeddings import embed_texts
from app.services.qdrant_client import search_similar_texts


async def retrieve_context(case: CaseInput) -> list[str]:
    s = get_settings()
    query_parts: list[str] = []
    query_parts.append(
        f"Age: {case.patient_age}, Sex: {case.sex}, Symptoms: {', '.join(case.symptoms)}"
    )
    if case.history:
        query_parts.append(f"History: {case.history}")
    if case.medications:
        query_parts.append(f"Medications: {', '.join(case.medications)}")
    query_text = " | ".join(query_parts)

    vectors = await embed_texts([query_text])
    query_vec = vectors[0]
    texts = search_similar_texts(
        collection=s.qdrant_collection,
        query_vector=query_vec,
        tenant_id=s.default_tenant_id,
        limit=5,
    )
    return texts
