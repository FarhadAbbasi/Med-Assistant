from app.schemas.case import CaseAnalysisResponse
from app.schemas.note import NoteSummaryResponse

DISCLAIMER = "This is not medical advice. Consult a qualified clinician if concerned, or escalate to emergency services for red-flag symptoms."

def apply_safety_postprocess(resp: CaseAnalysisResponse) -> CaseAnalysisResponse:
    resp.disclaimer = DISCLAIMER
    return resp

def apply_safety_note(resp: NoteSummaryResponse) -> NoteSummaryResponse:
    resp.disclaimer = DISCLAIMER
    return resp
