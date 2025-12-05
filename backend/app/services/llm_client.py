import httpx
from app.core.config import get_settings
from app.schemas.case import CaseInput, CaseAnalysisResponse
from app.schemas.note import NoteInput, NoteSummaryResponse

INSTRUCTIONS = (
    "You are a medical decision support assistant. Do not prescribe or dose. "
    "Provide structured case summary, differential diagnoses with uncertainty, red flags, and escalation advice. "
    "Include disclaimers."
)

class LLMClient:
    def __init__(self):
        self.s = get_settings()

    async def _chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=60.0) as client:
            resp = await client.post(
                f"{self.s.vllm_base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.s.vllm_api_key}"},
                json={
                    "model": self.s.vllm_model,
                    "messages": messages,
                    "temperature": 0.2,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            return data.get("choices", [{}])[0].get("message", {}).get("content", "")

    async def analyze_case(self, case: CaseInput, contexts: list[str]) -> CaseAnalysisResponse:
        prompt = (
            f"{INSTRUCTIONS}\n\nContext:\n" + "\n".join(contexts) +
            "\n\nPatient details:" 
            f" Age: {case.patient_age}, Sex: {case.sex}, Symptoms: {', '.join(case.symptoms)}."
        )
        content = await self._chat([
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": prompt},
        ])
        return CaseAnalysisResponse(
            summary=content[:500],
            differentials=[],
            red_flags=[],
            advice=[],
            disclaimer="This is not medical advice. Consult a qualified clinician.",
        )

    async def summarize_notes(self, note: NoteInput) -> NoteSummaryResponse:
        content = await self._chat([
            {"role": "system", "content": INSTRUCTIONS},
            {"role": "user", "content": f"Summarize clinically: {note.text}"},
        ])
        return NoteSummaryResponse(
            summary=content[:500],
            disclaimer="This is not medical advice. Consult a qualified clinician.",
        )
