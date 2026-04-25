from __future__ import annotations

from pathlib import Path
from typing import Optional

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Execution, ExecutionStep, Report, User
from app.security.auth_utils import require_permissions
from app.schemas.execution_schema import ExecutionOut, RunDemoRequest
from app.services.execution_service import ExecutionService

router = APIRouter(prefix="/executions", tags=["Executions"])

PROJECT_ROOT = Path(__file__).resolve().parents[3]
IMAGE_EXTENSIONS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}


def _resolve_local_file(raw_path: Optional[str]) -> Path:
    if not raw_path:
        raise HTTPException(status_code=404, detail="File path is empty.")
    candidate = Path(raw_path)
    if not candidate.is_absolute():
        candidate = PROJECT_ROOT / candidate
    resolved = candidate.resolve(strict=False)
    if not resolved.exists() or not resolved.is_file():
        raise HTTPException(status_code=404, detail=f"File not found: {raw_path}")
    return resolved


def _file_meta(raw_path: Optional[str]) -> dict:
    if not raw_path:
        return {"path": None, "filename": None, "exists": False, "size_bytes": 0, "is_image": False}
    filename = Path(raw_path).name
    is_image = Path(raw_path).suffix.lower() in IMAGE_EXTENSIONS
    try:
        resolved = _resolve_local_file(raw_path)
        return {
            "path": raw_path,
            "filename": filename,
            "exists": True,
            "size_bytes": resolved.stat().st_size,
            "is_image": is_image,
        }
    except HTTPException:
        return {"path": raw_path, "filename": filename, "exists": False, "size_bytes": 0, "is_image": is_image}


def _execution_dict(execution: Execution) -> dict:
    return {
        "id": execution.id,
        "execution_uid": execution.execution_uid,
        "project_name": execution.project_name,
        "suite_name": execution.suite_name,
        "test_name": execution.test_name,
        "execution_type": execution.execution_type,
        "browser": execution.browser,
        "environment": execution.environment,
        "base_url": execution.base_url,
        "headless": execution.headless,
        "status": execution.status,
        "started_at": execution.started_at,
        "finished_at": execution.finished_at,
        "duration_seconds": execution.duration_seconds,
        "total_steps": execution.total_steps,
        "passed_steps": execution.passed_steps,
        "failed_steps": execution.failed_steps,
        "skipped_steps": execution.skipped_steps,
        "success_percentage": execution.success_percentage,
        "message": execution.message,
        "created_at": execution.created_at.isoformat() if execution.created_at else None,
    }


def _step_dict(step: ExecutionStep, execution_id: int) -> dict:
    evidence = _file_meta(step.screenshot_path)
    return {
        "id": step.id,
        "execution_id": step.execution_id,
        "step_order": step.step_order,
        "name": step.name,
        "action": step.action,
        "selector": step.selector,
        "status": step.status,
        "message": step.message,
        "duration_seconds": step.duration_seconds,
        "error_detail": step.error_detail,
        "created_at": step.created_at.isoformat() if step.created_at else None,
        "screenshot_path": step.screenshot_path,
        "evidence": evidence,
        "view_evidence_url": f"/api/executions/{execution_id}/steps/{step.id}/evidence/view" if evidence["exists"] and evidence["is_image"] else None,
        "download_evidence_url": f"/api/executions/{execution_id}/steps/{step.id}/evidence/download" if evidence["exists"] else None,
    }


def _report_dict(report: Optional[Report]) -> Optional[dict]:
    if not report:
        return None
    return {
        "id": report.id,
        "execution_id": report.execution_id,
        "created_at": report.created_at.isoformat() if report.created_at else None,
        "html": _file_meta(report.html_path),
        "excel": _file_meta(report.excel_path),
        "pdf": _file_meta(report.pdf_path),
        "html_view_url": f"/api/reports/{report.id}/view/html" if report.html_path else None,
        "html_download_url": f"/api/reports/{report.id}/download/html" if report.html_path else None,
        "excel_download_url": f"/api/reports/{report.id}/download/excel" if report.excel_path else None,
        "pdf_download_url": f"/api/reports/{report.id}/download/pdf" if report.pdf_path else None,
    }


@router.get("", response_model=list[ExecutionOut])
def list_executions(db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["executions.view"]))):
    return ExecutionService(db).list_executions()


@router.get("/compare")
def compare_executions(
    left_id: int = Query(...),
    right_id: int = Query(...),
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["executions.view"])),
):
    left = ExecutionService(db).get_execution(left_id)
    right = ExecutionService(db).get_execution(right_id)
    if not left or not right:
        raise HTTPException(status_code=404, detail="One or both executions were not found")

    def metrics(exe: Execution) -> dict:
        return {
            "status": exe.status,
            "success_percentage": exe.success_percentage,
            "duration_seconds": exe.duration_seconds,
            "total_steps": exe.total_steps,
            "passed_steps": exe.passed_steps,
            "failed_steps": exe.failed_steps,
            "skipped_steps": exe.skipped_steps,
        }

    return {
        "left": _execution_dict(left),
        "right": _execution_dict(right),
        "left_metrics": metrics(left),
        "right_metrics": metrics(right),
        "delta": {
            "success_percentage": round((right.success_percentage or 0) - (left.success_percentage or 0), 2),
            "duration_seconds": round((right.duration_seconds or 0) - (left.duration_seconds or 0), 2),
            "failed_steps": (right.failed_steps or 0) - (left.failed_steps or 0),
            "passed_steps": (right.passed_steps or 0) - (left.passed_steps or 0),
        },
    }


@router.get("/{execution_id}", response_model=ExecutionOut)
def get_execution(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["executions.view"]))):
    execution = ExecutionService(db).get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    return execution


@router.get("/{execution_id}/trace")
def get_execution_trace(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["executions.view"]))):
    execution = ExecutionService(db).get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")

    steps = db.query(ExecutionStep).filter(ExecutionStep.execution_id == execution_id).order_by(ExecutionStep.step_order.asc()).all()
    step_payload = [_step_dict(step, execution_id) for step in steps]
    failures = [step for step in step_payload if step.get("status") == "FAILED"]
    evidences = [step for step in step_payload if step.get("evidence", {}).get("exists")]
    timeline = [
        {
            "order": step["step_order"],
            "label": step["name"],
            "status": step["status"],
            "duration_seconds": step["duration_seconds"],
        }
        for step in step_payload
    ]
    return {
        "execution": _execution_dict(execution),
        "steps": step_payload,
        "failures": failures,
        "evidences": evidences,
        "timeline": timeline,
        "report": _report_dict(execution.report),
        "summary": {
            "has_failures": len(failures) > 0,
            "evidence_count": len(evidences),
            "longest_step": max(step_payload, key=lambda item: item.get("duration_seconds") or 0) if step_payload else None,
        },
    }


@router.get("/{execution_id}/steps")
def get_execution_steps(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["executions.view"]))):
    execution = ExecutionService(db).get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    steps = db.query(ExecutionStep).filter(ExecutionStep.execution_id == execution_id).order_by(ExecutionStep.step_order.asc()).all()
    return [_step_dict(step, execution_id) for step in steps]


@router.get("/{execution_id}/logs")
def get_execution_logs(execution_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["executions.view"]))):
    execution = ExecutionService(db).get_execution(execution_id)
    if not execution:
        raise HTTPException(status_code=404, detail="Execution not found")
    steps = db.query(ExecutionStep).filter(ExecutionStep.execution_id == execution_id).order_by(ExecutionStep.step_order.asc()).all()
    lines = []
    if execution.message:
        lines.append(f"[SUMMARY] {execution.message}")
    for step in steps:
        msg = step.message or ""
        err = f" | ERROR: {step.error_detail}" if step.error_detail else ""
        lines.append(f"[{step.status}] Step {step.step_order} - {step.name} ({step.action}) {msg}{err}")
    return {"execution_id": execution_id, "lines": lines}


@router.get("/{execution_id}/steps/{step_id}/evidence/view")
def view_execution_step_evidence(
    execution_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.view"])),
):
    step = db.query(ExecutionStep).filter(ExecutionStep.id == step_id, ExecutionStep.execution_id == execution_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step evidence not found")
    evidence = _file_meta(step.screenshot_path)
    if not evidence["is_image"]:
        raise HTTPException(status_code=400, detail="Evidence is not an image")
    file_path = _resolve_local_file(step.screenshot_path)
    return FileResponse(str(file_path), media_type="image/png")


@router.get("/{execution_id}/steps/{step_id}/evidence/download")
def download_execution_step_evidence(
    execution_id: int,
    step_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.download"])),
):
    step = db.query(ExecutionStep).filter(ExecutionStep.id == step_id, ExecutionStep.execution_id == execution_id).first()
    if not step:
        raise HTTPException(status_code=404, detail="Step evidence not found")
    file_path = _resolve_local_file(step.screenshot_path)
    return FileResponse(str(file_path), filename=file_path.name)


@router.post("/run-demo", response_model=ExecutionOut)
def run_demo(request: RunDemoRequest, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["executions.run"]))):
    return ExecutionService(db).run_demo(request)
