from pydantic import BaseModel

class Differential(BaseModel):
    condition: str
    probability: float

class Advice(BaseModel):
    text: str

class RedFlag(BaseModel):
    text: str
