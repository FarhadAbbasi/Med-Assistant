from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import (
    Boolean,
    Column,
    DateTime,
    ForeignKey,
    String,
    Text,
    Integer,
)
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship

from app.db.session import Base


class TimestampMixin:
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)
    updated_at = Column(
        DateTime(timezone=True), default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )


class Tenant(Base, TimestampMixin):
    __tablename__ = "tenants"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    slug = Column(String(64), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    plan = Column(String(32), nullable=True)

    users = relationship("User", back_populates="tenant", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="tenant", cascade="all, delete-orphan")


class User(Base, TimestampMixin):
    __tablename__ = "users"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)

    email = Column(String(255), nullable=False)
    hashed_password = Column(String(255), nullable=False)
    role = Column(String(32), nullable=False, default="doctor")
    is_active = Column(Boolean, nullable=False, default=True)

    tenant = relationship("Tenant", back_populates="users")
    cases = relationship("Case", back_populates="created_by")


class Case(Base, TimestampMixin):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    created_by_user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    patient_age = Column(Integer, nullable=False)
    sex = Column(String(16), nullable=False)
    symptoms = Column(JSONB, nullable=False)
    history = Column(Text, nullable=True)
    medications = Column(JSONB, nullable=True)
    vitals = Column(JSONB, nullable=True)

    status = Column(String(32), nullable=False, default="open")

    tenant = relationship("Tenant", back_populates="cases")
    created_by = relationship("User", back_populates="cases")
    interactions = relationship("Interaction", back_populates="case", cascade="all, delete-orphan")


class Interaction(Base):
    __tablename__ = "interactions"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    case_id = Column(UUID(as_uuid=True), ForeignKey("cases.id"), nullable=False, index=True)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    request_payload = Column(JSONB, nullable=False)
    response_payload = Column(JSONB, nullable=False)
    llm_model = Column(String(255), nullable=False)
    latency_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    case = relationship("Case", back_populates="interactions")
    tenant = relationship("Tenant")
    user = relationship("User")


class AuditLog(Base):
    __tablename__ = "audit_logs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    tenant_id = Column(UUID(as_uuid=True), ForeignKey("tenants.id"), nullable=False, index=True)
    user_id = Column(UUID(as_uuid=True), ForeignKey("users.id"), nullable=True)

    action = Column(String(64), nullable=False)
    details = Column(JSONB, nullable=True)
    created_at = Column(DateTime(timezone=True), default=datetime.utcnow, nullable=False)

    tenant = relationship("Tenant")
    user = relationship("User")
