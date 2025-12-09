from __future__ import annotations

from datetime import timedelta

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import verify_password, get_password_hash, create_access_token
from app.core.deps import get_current_user
from app.db.session import get_db
from app.db import models
from app.schemas.auth import LoginRequest, TokenResponse, UserRead


router = APIRouter()


@router.post("/login", response_model=TokenResponse)
async def login(payload: LoginRequest, db: Session = Depends(get_db)):
    settings = get_settings()

    user = (
        db.query(models.User)
        .join(models.Tenant, models.User.tenant_id == models.Tenant.id)
        .filter(models.User.email == payload.email)
        .one_or_none()
    )
    if user is None or not verify_password(payload.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Incorrect email or password")

    access_token = create_access_token(
        data={"sub": str(user.id), "tenant_id": str(user.tenant_id), "role": user.role},
        expires_delta=timedelta(hours=8),
    )
    return TokenResponse(access_token=access_token)


@router.get("/me", response_model=UserRead)
async def read_me(current_user: models.User = Depends(get_current_user)):
    return UserRead.from_orm(current_user)
