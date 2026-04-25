from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.schemas.settings_schema import SettingsPayload, SettingsResponse
from app.security.auth_utils import require_permissions, get_current_user
from app.services.audit_service import write_audit_log
from app.services.settings_service import get_settings_payload, update_settings, reset_settings

router = APIRouter(prefix="/settings", tags=["Settings"])


@router.get("/public")
def get_public_settings(db: Session = Depends(get_db)):
    payload = get_settings_payload(db).model_dump()
    payload["smtp_password"] = ""
    return payload


@router.get("", response_model=SettingsResponse)
def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["settings.manage"])),
):
    payload = get_settings_payload(db).model_dump()
    payload["smtp_password"] = ""
    return payload


@router.put("", response_model=SettingsResponse)
def save_settings(
    payload: SettingsPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["settings.manage"])),
):
    updated = update_settings(db, payload)
    write_audit_log(
        db,
        action="SETTINGS_UPDATED",
        module="Settings",
        user=current_user,
        request=request,
        description="Global settings and white label configuration updated.",
    )
    data = updated.model_dump()
    data["smtp_password"] = ""
    return data


@router.post("/reset", response_model=SettingsResponse)
def reset_global_settings(
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["settings.manage"])),
):
    updated = reset_settings(db)
    write_audit_log(
        db,
        action="SETTINGS_RESET",
        module="Settings",
        user=current_user,
        request=request,
        description="Global settings were restored to defaults.",
    )
    data = updated.model_dump()
    data["smtp_password"] = ""
    return data
