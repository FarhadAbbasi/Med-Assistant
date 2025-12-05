from pydantic import BaseModel

class NoteInput(BaseModel):
    text: str

class NoteSummaryResponse(BaseModel):
    summary: str
    disclaimer: str
