from fastapi import FastAPI, Header
from pydantic import BaseModel

app = FastAPI(title="LLM Stub")

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    model: str
    messages: list[ChatMessage]
    temperature: float | None = 0.2

@app.get("/health")
async def health():
    return {"status": "ok"}

@app.post("/v1/chat/completions")
async def chat(req: ChatRequest, authorization: str | None = Header(default=None)):
    content = "Stubbed response. " + (req.messages[-1].content if req.messages else "")
    return {
        "id": "chatcmpl-stub",
        "object": "chat.completion",
        "choices": [
            {
                "index": 0,
                "message": {"role": "assistant", "content": content},
                "finish_reason": "stop",
            }
        ],
        "created": 0,
        "model": req.model,
    }
