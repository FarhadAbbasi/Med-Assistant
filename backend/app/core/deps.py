from __future__ import annotations

from typing import Annotated

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.orm import Session

from app.core.config import get_settings
from app.core.security import decode_access_token
from app.db.session import get_db
from app.db import models


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


DbSession = Annotated[Session, Depends(get_db)]


def get_current_user(
    db: DbSession,
    token: Annotated[str, Depends(oauth2_scheme)],
) -> models.User:
    settings = get_settings()
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = decode_access_token(token)
        user_id: str | None = payload.get("sub")
        tenant_id: str | None = payload.get("tenant_id")
        if user_id is None or tenant_id is None:
            raise credentials_exception
    except Exception:
        raise credentials_exception

    user = (
        db.query(models.User)
        .filter(models.User.id == user_id, models.User.tenant_id == tenant_id, models.User.is_active.is_(True))
        .one_or_none()
    )
    if user is None:
        raise credentials_exception
    return user


def get_current_tenant(
    db: DbSession,
    current_user: Annotated[models.User, Depends(get_current_user)],
) -> models.Tenant:
    tenant = db.query(models.Tenant).filter(models.Tenant.id == current_user.tenant_id).one_or_none()
    if tenant is None:
        raise HTTPException(status_code=400, detail="Tenant not found")
    return tenant
