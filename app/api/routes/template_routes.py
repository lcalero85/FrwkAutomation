from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.security.auth_utils import require_permissions
from app.schemas.template_schema import TemplateApplyRequest, TemplateApplyResponse, TemplateCreate, TemplateOut, TemplateUpdate
from app.services.template_service import TemplateService

router = APIRouter(prefix="/templates", tags=["Templates"])


@router.get("", response_model=list[TemplateOut])
def list_templates(
    template_type: str | None = Query(default=None),
    category: str | None = Query(default=None),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["templates.view"])),
):
    return TemplateService(db).list_templates(template_type=template_type, category=category)


@router.get("/{template_id}", response_model=TemplateOut)
def get_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["templates.view"])),
):
    template = TemplateService(db).get_template(template_id)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.post("", response_model=TemplateOut, status_code=201)
def create_template(
    data: TemplateCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["templates.manage"])),
):
    return TemplateService(db).create_template(data)


@router.put("/{template_id}", response_model=TemplateOut)
def update_template(
    template_id: int,
    data: TemplateUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["templates.manage"])),
):
    template = TemplateService(db).update_template(template_id, data)
    if not template:
        raise HTTPException(status_code=404, detail="Template not found")
    return template


@router.delete("/{template_id}")
def delete_template(
    template_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["templates.manage"])),
):
    try:
        deleted = TemplateService(db).delete_template(template_id)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not deleted:
        raise HTTPException(status_code=404, detail="Template not found")
    return {"deleted": True}


@router.post("/{template_id}/apply", response_model=TemplateApplyResponse)
def apply_template(
    template_id: int,
    data: TemplateApplyRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["templates.apply"])),
):
    result = TemplateService(db).apply_template(template_id, data)
    if not result:
        raise HTTPException(status_code=404, detail="Template not found")
    return result
