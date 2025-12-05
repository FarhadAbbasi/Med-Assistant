from fastapi import FastAPI, Depends, Header
from app.core.config import Settings, get_settings
from app.api.v1.routes_health import router as health_router
from app.api.v1.routes_cases import router as cases_router
from app.api.v1.routes_notes import router as notes_router
from app.api.v1.routes_documents import router as documents_router

app = FastAPI(title="Medical Assistant API", version="0.1.0")

@app.middleware("http")
async def tenant_middleware(request, call_next):
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"status": "ok"}

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(cases_router, prefix="/api/v1/cases", tags=["cases"])
app.include_router(notes_router, prefix="/api/v1/notes", tags=["notes"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
