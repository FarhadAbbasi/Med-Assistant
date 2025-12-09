from __future__ import annotations

import json
from pathlib import Path
from typing import Dict


DEFAULT_SYSTEM_PROMPT = (
    "You are a medical decision support assistant. Do not prescribe or dose. "
    "Provide structured case summary, differential diagnoses with uncertainty, red flags, and escalation advice. "
    "Include disclaimers."
)


_SETTINGS_PATH = Path(__file__).parent / "admin_settings.json"


def load_admin_settings() -> Dict[str, str]:
    if _SETTINGS_PATH.exists():
        try:
            data = json.loads(_SETTINGS_PATH.read_text(encoding="utf-8"))
            if isinstance(data, dict) and "system_prompt" in data:
                return {"system_prompt": str(data["system_prompt"])}
        except Exception:
            pass
    return {"system_prompt": DEFAULT_SYSTEM_PROMPT}


def save_admin_settings(system_prompt: str) -> None:
    data = {"system_prompt": system_prompt}
    _SETTINGS_PATH.write_text(json.dumps(data, ensure_ascii=False, indent=2), encoding="utf-8")
