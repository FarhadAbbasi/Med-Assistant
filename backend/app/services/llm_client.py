import re

import httpx
from app.core.config import get_settings
from app.schemas.case import CaseInput, CaseAnalysisResponse
from app.schemas.note import NoteInput, NoteSummaryResponse
from app.core.admin_settings import load_admin_settings


def _strip_think(content: str) -> str:
    """Remove <think>...</think> blocks from model output."""
    return re.sub(r"<think>[\s\S]*?</think>", "", content).strip()


class LLMClient:
    def __init__(self):
        self.s = get_settings()

    async def _chat(self, messages: list[dict]) -> str:
        async with httpx.AsyncClient(timeout=120.0) as client:
            resp = await client.post(
                f"{self.s.vllm_base_url}/v1/chat/completions",
                headers={"Authorization": f"Bearer {self.s.vllm_api_key}"},
                json={
                    "model": self.s.vllm_model,
                    "messages": messages,
                    "temperature": 0.2,
                    "max_tokens": 768,
                },
            )
            resp.raise_for_status()
            data = resp.json()
            raw = data.get("choices", [{}])[0].get("message", {}).get("content", "")
            return _strip_think(raw)

    async def analyze_case(self, case: CaseInput, contexts: list[str]) -> CaseAnalysisResponse:
        system_prompt = load_admin_settings()["system_prompt"]
        prompt = (
            f"{system_prompt}\n\nContext:\n" + "\n".join(contexts) +
            "\n\nPatient details:" 
            f" Age: {case.patient_age}, Sex: {case.sex}, Symptoms: {', '.join(case.symptoms)}."
        )
        content = await self._chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": prompt},
        ])
        return CaseAnalysisResponse(
            summary=content,
            differentials=[],
            red_flags=[],
            advice=[],
            disclaimer="This is not medical advice. Consult a qualified clinician.",
        )

    async def summarize_notes(self, note: NoteInput) -> NoteSummaryResponse:
        system_prompt = load_admin_settings()["system_prompt"]
        content = await self._chat([
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Summarize clinically: {note.text}"},
        ])
        return NoteSummaryResponse(
            summary=content,
            disclaimer="This is not medical advice. Consult a qualified clinician.",
        )
