from fastapi import FastAPI, Depends, Header
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
from pathlib import Path

from app.core.config import Settings, get_settings
from app.api.v1.routes_health import router as health_router
from app.api.v1.routes_cases import router as cases_router
from app.api.v1.routes_notes import router as notes_router
from app.api.v1.routes_documents import router as documents_router
from app.api.v1.routes_auth import router as auth_router
from app.api.v1.routes_admin import router as admin_router
from app.api.v1.routes_chat import router as chat_router

app = FastAPI(title="Medical Assistant API", version="0.1.0")

static_dir = Path(__file__).parent / "static"
if static_dir.exists():
    app.mount("/static", StaticFiles(directory=str(static_dir)), name="static")

@app.middleware("http")
async def tenant_middleware(request, call_next):
    response = await call_next(request)
    return response

@app.get("/")
async def root():
    return {"status": "ok"}


@app.get("/demo")
async def demo_page():
    file_path = static_dir / "demo.html"
    return FileResponse(file_path)


@app.get("/admin")
async def admin_page():
    file_path = static_dir / "admin.html"
    return FileResponse(file_path)

app.include_router(health_router, prefix="/health", tags=["health"])
app.include_router(auth_router, prefix="/auth", tags=["auth"])
app.include_router(admin_router, prefix="/admin", tags=["admin"])
app.include_router(chat_router, prefix="/api/v1", tags=["chat"])
app.include_router(cases_router, prefix="/api/v1/cases", tags=["cases"])
app.include_router(notes_router, prefix="/api/v1/notes", tags=["notes"])
app.include_router(documents_router, prefix="/api/v1/documents", tags=["documents"])
