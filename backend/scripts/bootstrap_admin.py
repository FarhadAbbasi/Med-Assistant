from __future__ import annotations

"""One-off script to create a default tenant and admin user.

Run with:

  cd backend
  ..\.venv\Scripts\Activate.ps1  # on Windows PowerShell
  python -m scripts.bootstrap_admin

This will:
- Ensure tenant with slug "public" exists.
- Ensure admin user admin@example.com exists for that tenant.
"""

from app.db.session import SessionLocal
from app.db import models
from app.core.security import get_password_hash


DEFAULT_TENANT_SLUG = "public"
DEFAULT_TENANT_NAME = "Public Tenant"
DEFAULT_ADMIN_EMAIL = "x.farhad55@gmail.com"
DEFAULT_ADMIN_PASSWORD = "Xfarhad55"  # change later in a real system


def main() -> None:
    db = SessionLocal()
    try:
        tenant = db.query(models.Tenant).filter_by(slug=DEFAULT_TENANT_SLUG).one_or_none()
        if tenant is None:
            tenant = models.Tenant(slug=DEFAULT_TENANT_SLUG, name=DEFAULT_TENANT_NAME)
            db.add(tenant)
            db.commit()
            db.refresh(tenant)
            print(f"Created tenant: {tenant.id} ({tenant.slug})")
        else:
            print(f"Tenant already exists: {tenant.id} ({tenant.slug})")

        user = (
            db.query(models.User)
            .filter_by(email=DEFAULT_ADMIN_EMAIL, tenant_id=tenant.id)
            .one_or_none()
        )
        if user is None:
            user = models.User(
                tenant_id=tenant.id,
                email=DEFAULT_ADMIN_EMAIL,
                hashed_password=get_password_hash(DEFAULT_ADMIN_PASSWORD),
                role="admin",
                is_active=True,
            )
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Created admin user: {user.id} ({user.email})")
        else:
            # Always refresh password hash so it matches current hashing scheme.
            user.hashed_password = get_password_hash(DEFAULT_ADMIN_PASSWORD)
            user.role = "admin"
            user.is_active = True
            db.add(user)
            db.commit()
            db.refresh(user)
            print(f"Updated admin user password: {user.id} ({user.email})")

        print("\nLogin credentials:")
        print(f"  email:    {DEFAULT_ADMIN_EMAIL}")
        print(f"  password: {DEFAULT_ADMIN_PASSWORD}")

    finally:
        db.close()


if __name__ == "__main__":
    main()
