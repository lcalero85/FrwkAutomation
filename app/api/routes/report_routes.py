from __future__ import annotations

import mimetypes
from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import ExecutionStep, Report, User
from app.security.auth_utils import require_permissions

router = APIRouter(prefix="/reports", tags=["Reports"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]


REPORT_TYPE_MAP = {
    "html": ("html_path", "text/html"),
    "excel": ("excel_path", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "xlsx": ("excel_path", "application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"),
    "pdf": ("pdf_path", "application/pdf"),
}

IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _resolve_project_file(raw_path: Optional[str]) -> Path:
    """Resolve a stored report/evidence path safely for local download/preview."""
    if not raw_path:
        raise HTTPException(status_code=404, detail="File path is empty.")

    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate

    # Resolve when possible. strict=False allows clearer custom error if missing.
    resolved = candidate.resolve(strict=False)
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {raw_path}")

    return resolved


def _file_payload(path_value: Optional[str]) -> dict:
    exists = False
    size_bytes = 0
    filename = None
    if path_value:
        try:
            resolved = _resolve_project_file(path_value)
            exists = True
            size_bytes = resolved.stat().st_size
            filename = resolved.name
        except HTTPException:
            filename = Path(path_value).name
    return {
        "path": path_value,
        "filename": filename,
        "exists": exists,
        "size_bytes": size_bytes,
    }


def _report_to_dict(report: Report) -> dict:
    execution = report.execution
    return {
        "id": report.id,
        "execution_id": report.execution_id,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "html_path": report.html_path,
        "excel_path": report.excel_path,
        "pdf_path": report.pdf_path,
        "files": {
            "html": _file_payload(report.html_path),
            "excel": _file_payload(report.excel_path),
            "pdf": _file_payload(report.pdf_path),
        },
        "execution": {
            "id": execution.id if execution else None,
            "execution_uid": execution.execution_uid if execution else None,
            "project_name": execution.project_name if execution else None,
            "suite_name": execution.suite_name if execution else None,
            "test_name": execution.test_name if execution else None,
            "browser": execution.browser if execution else None,
            "environment": execution.environment if execution else None,
            "status": execution.status if execution else None,
            "duration_seconds": execution.duration_seconds if execution else 0,
            "success_percentage": execution.success_percentage if execution else 0,
            "total_steps": execution.total_steps if execution else 0,
            "passed_steps": execution.passed_steps if execution else 0,
            "failed_steps": execution.failed_steps if execution else 0,
            "skipped_steps": execution.skipped_steps if execution else 0,
        },
    }


@router.get("")
def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.view"])),
):
    reports = db.query(Report).order_by(Report.id.desc()).all()
    return [_report_to_dict(report) for report in reports]


@router.get("/{report_id}")
def get_report_detail(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.view"])),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    return _report_to_dict(report)


@router.get("/{report_id}/download/{file_type}")
def download_report_file(
    report_id: int,
    file_type: str,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.download"])),
):
    normalized_type = file_type.lower()
    if normalized_type not in REPORT_TYPE_MAP:
        raise HTTPException(status_code=400, detail="Invalid file type. Use html, excel or pdf.")

    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    field_name, media_type = REPORT_TYPE_MAP[normalized_type]
    file_path = _resolve_project_file(getattr(report, field_name))
    return FileResponse(
        path=str(file_path),
        filename=file_path.name,
        media_type=media_type,
    )


@router.get("/{report_id}/view/html")
def view_html_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.view"])),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")
    file_path = _resolve_project_file(report.html_path)
    return FileResponse(path=str(file_path), media_type="text/html")


@router.get("/{report_id}/evidences")
def list_report_evidences(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.view"])),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    steps = (
        db.query(ExecutionStep)
        .filter(ExecutionStep.execution_id == report.execution_id)
        .order_by(ExecutionStep.step_order.asc())
        .all()
    )

    evidences = []
    for step in steps:
        path_value = step.screenshot_path
        exists = False
        filename = None
        size_bytes = 0
        is_image = False
        if path_value:
            filename = Path(path_value).name
            is_image = Path(path_value).suffix.lower() in IMAGE_EXTENSIONS
            try:
                resolved = _resolve_project_file(path_value)
                exists = True
                size_bytes = resolved.stat().st_size
            except HTTPException:
                pass

        evidences.append(
            {
                "step_id": step.id,
                "step_order": step.step_order,
                "name": step.name,
                "action": step.action,
                "selector": step.selector,
                "status": step.status,
                "message": step.message,
                "screenshot_path": path_value,
                "filename": filename,
                "exists": exists,
                "is_image": is_image,
                "size_bytes": size_bytes,
                "view_url": f"/api/reports/{report_id}/evidences/{step.id}/view" if exists and is_image else None,
                "download_url": f"/api/reports/{report_id}/evidences/{step.id}/download" if exists else None,
            }
        )
    return evidences


@router.get("/{report_id}/evidences/{step_id}/view")
def view_step_evidence(
    report_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.view"])),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    step = (
        db.query(ExecutionStep)
        .filter(ExecutionStep.id == step_id, ExecutionStep.execution_id == report.execution_id)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Evidence step not found.")

    file_path = _resolve_project_file(step.screenshot_path)
    if file_path.suffix.lower() not in IMAGE_EXTENSIONS:
        raise HTTPException(status_code=400, detail="Evidence is not a supported image.")

    media_type = mimetypes.guess_type(file_path.name)[0] or "image/png"
    return FileResponse(path=str(file_path), media_type=media_type)


@router.get("/{report_id}/evidences/{step_id}/download")
def download_step_evidence(
    report_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.download"])),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Report not found.")

    step = (
        db.query(ExecutionStep)
        .filter(ExecutionStep.id == step_id, ExecutionStep.execution_id == report.execution_id)
        .first()
    )
    if not step:
        raise HTTPException(status_code=404, detail="Evidence step not found.")

    file_path = _resolve_project_file(step.screenshot_path)
    return FileResponse(path=str(file_path), filename=file_path.name)
