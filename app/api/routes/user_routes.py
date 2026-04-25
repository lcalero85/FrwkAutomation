from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.schemas.security_schema import AuditLogResponse
from app.schemas.user_schema import RoleResponse, UserCreateRequest, UserResponse, UserUpdateRequest
from app.security.auth_utils import require_permissions, require_roles
from app.services import user_service
from app.services.audit_service import list_audit_logs, write_audit_log

router = APIRouter(tags=["Users, Roles and Security"])


@router.get("/users", response_model=list[UserResponse])
def get_users(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["users.manage"])),
):
    return user_service.list_users(db)


@router.post("/users", response_model=UserResponse)
def create_user(
    payload: UserCreateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["users.manage"])),
):
    user = user_service.create_user(db, payload)
    write_audit_log(
        db,
        action="USER_CREATED",
        module="Users",
        user=current_user,
        description=f"Created user {user['username']}.",
        request=request,
        status="SUCCESS",
    )
    return user


@router.put("/users/{user_id}", response_model=UserResponse)
def update_user(
    user_id: int,
    payload: UserUpdateRequest,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["users.manage"])),
):
    user = user_service.update_user(db, user_id, payload)
    write_audit_log(
        db,
        action="USER_UPDATED",
        module="Users",
        user=current_user,
        description=f"Updated user {user['username']}.",
        request=request,
        status="SUCCESS",
    )
    return user


@router.get("/roles", response_model=list[RoleResponse])
def get_roles(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_roles(["Administrador", "QA Lead", "QA Automation", "Viewer"])),
):
    return user_service.list_roles(db)


@router.get("/audit-logs", response_model=list[AuditLogResponse])
def get_audit_logs(
    limit: int = 100,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["security.audit"])),
):
    return list_audit_logs(db, limit=limit)
