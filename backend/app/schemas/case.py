from pydantic import BaseModel, Field
from typing import List
from app.schemas.common import Differential, Advice, RedFlag

class CaseInput(BaseModel):
    patient_age: int
    sex: str
    symptoms: list[str]
    history: str | None = None
    medications: list[str] | None = None
    vitals: dict | None = None

class CaseAnalysisResponse(BaseModel):
    summary: str
    differentials: List[Differential]
    red_flags: List[RedFlag]
    advice: List[Advice]
    uncertainty: float = Field(ge=0.0, le=1.0, default=0.3)
    disclaimer: str
