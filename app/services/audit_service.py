from __future__ import annotations

from typing import Optional

from fastapi import Request
from sqlalchemy.orm import Session

from app.database.models import AuditLog, User


def get_client_ip(request: Optional[Request]) -> Optional[str]:
    if not request:
        return None
    forwarded_for = request.headers.get("x-forwarded-for")
    if forwarded_for:
        return forwarded_for.split(",")[0].strip()
    return request.client.host if request.client else None


def write_audit_log(
    db: Session,
    *,
    action: str,
    module: str,
    description: str | None = None,
    user: User | None = None,
    username: str | None = None,
    request: Request | None = None,
    status: str = "SUCCESS",
) -> AuditLog:
    log = AuditLog(
        user_id=user.id if user else None,
        username=user.username if user else username,
        action=action,
        module=module,
        description=description,
        ip_address=get_client_ip(request),
        status=status,
    )
    db.add(log)
    db.commit()
    db.refresh(log)
    return log


def list_audit_logs(db: Session, limit: int = 100) -> list[AuditLog]:
    limit = max(1, min(limit, 500))
    return db.query(AuditLog).order_by(AuditLog.id.desc()).limit(limit).all()
