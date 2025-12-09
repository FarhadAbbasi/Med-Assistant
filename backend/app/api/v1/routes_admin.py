from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel

from app.core.deps import get_current_user
from app.db.session import get_db
from app.db import models
from app.core.admin_settings import load_admin_settings, save_admin_settings


router = APIRouter()


def _ensure_admin(user: models.User) -> None:
    if user.role != "admin":
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Admin access required")


class AdminSettings(BaseModel):
    system_prompt: str


@router.get("/summary")
async def admin_summary(db: Session = Depends(get_db), current_user: models.User = Depends(get_current_user)):
    _ensure_admin(current_user)

    tenants = db.query(models.Tenant).all()
    users = db.query(models.User).all()
    cases = db.query(models.Case).all()
    interactions = db.query(models.Interaction).order_by(models.Interaction.created_at.desc()).limit(50).all()

    return {
        "tenants": [
            {"id": str(t.id), "slug": t.slug, "name": t.name, "plan": t.plan}
            for t in tenants
        ],
        "users": [
            {
                "id": str(u.id),
                "email": u.email,
                "tenant_id": str(u.tenant_id),
                "role": u.role,
                "is_active": u.is_active,
            }
            for u in users
        ],
        "cases": [
            {
                "id": str(c.id),
                "tenant_id": str(c.tenant_id),
                "created_by_user_id": str(c.created_by_user_id) if c.created_by_user_id else None,
                "patient_age": c.patient_age,
                "sex": c.sex,
                "status": c.status,
            }
            for c in cases
        ],
        "interactions": [
            {
                "id": str(i.id),
                "case_id": str(i.case_id),
                "tenant_id": str(i.tenant_id),
                "user_id": str(i.user_id) if i.user_id else None,
                "llm_model": i.llm_model,
                "created_at": i.created_at.isoformat() if i.created_at else None,
            }
            for i in interactions
        ],
    }


@router.get("/settings", response_model=AdminSettings)
async def get_admin_settings(current_user: models.User = Depends(get_current_user)) -> AdminSettings:
    _ensure_admin(current_user)
    data = load_admin_settings()
    return AdminSettings(system_prompt=data["system_prompt"])


@router.put("/settings", response_model=AdminSettings)
async def update_admin_settings(payload: AdminSettings, current_user: models.User = Depends(get_current_user)) -> AdminSettings:
    _ensure_admin(current_user)
    save_admin_settings(payload.system_prompt)
    return payload
