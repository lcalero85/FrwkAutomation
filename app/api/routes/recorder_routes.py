from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import FileResponse
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import User
from app.security.auth_utils import require_permissions
from app.schemas.execution_schema import ExecutionOut, RunRecordedCaseRequest
from app.schemas.recorder_schema import (
    GeneratedCodeOut,
    RecordedCaseCreate,
    RecordedCaseOut,
    RecordedCaseUpdate,
    RecordedStepCreate,
    RecordedStepOut,
    RecordedStepUpdate,
    SelectorSuggestionOut,
    SelectorSuggestionRequest,
    BrowserRecordedEventIn,
    BrowserRecorderInstructionOut,
    BrowserRecorderStatusOut,
    RecorderCleanupOut,
    RecordedCaseExportPreviewOut,
    RecordedCaseExportOut,
)
from app.services.recorder_service import RecorderService
from app.services.recorded_execution_service import RecordedExecutionService
from app.services.code_export_service import CodeExportService

router = APIRouter(prefix="/recorder", tags=["Recorder"])


@router.get("/cases", response_model=list[RecordedCaseOut])
def list_cases(db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    return RecorderService(db).list_cases()


@router.post("/cases", response_model=RecordedCaseOut, status_code=201)
def create_case(data: RecordedCaseCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    return RecorderService(db).create_case(data)


@router.get("/cases/{case_id}", response_model=RecordedCaseOut)
def get_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    case = RecorderService(db).get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return case


@router.put("/cases/{case_id}", response_model=RecordedCaseOut)
def update_case(case_id: int, data: RecordedCaseUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    case = RecorderService(db).update_case(case_id, data)
    if not case:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return case


@router.delete("/cases/{case_id}")
def delete_case(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    deleted = RecorderService(db).delete_case(case_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return {"deleted": True}


@router.post("/cases/{case_id}/steps", response_model=RecordedStepOut, status_code=201)
def add_step(case_id: int, data: RecordedStepCreate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    step = RecorderService(db).add_step(case_id, data)
    if not step:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return step


@router.put("/steps/{step_id}", response_model=RecordedStepOut)
def update_step(step_id: int, data: RecordedStepUpdate, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    step = RecorderService(db).update_step(step_id, data)
    if not step:
        raise HTTPException(status_code=404, detail="Recorded step not found")
    return step


@router.delete("/steps/{step_id}")
def delete_step(step_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    deleted = RecorderService(db).delete_step(step_id)
    if not deleted:
        raise HTTPException(status_code=404, detail="Recorded step not found")
    return {"deleted": True}


@router.post("/cases/{case_id}/reorder", response_model=RecordedCaseOut)
def reorder_steps(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    case = RecorderService(db).reorder_steps(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return case


@router.post("/selector-suggestions", response_model=list[SelectorSuggestionOut])
def selector_suggestions(data: SelectorSuggestionRequest, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    return RecorderService(db).suggest_selectors(data)


@router.get("/cases/{case_id}/code", response_model=GeneratedCodeOut)
def generate_code(case_id: int, db: Session = Depends(get_db), current_user: User = Depends(require_permissions(["recorder.manage"]))):
    code = RecorderService(db).generate_python_code(case_id)
    if code is None:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return GeneratedCodeOut(recorded_case_id=case_id, code=code)




@router.get("/cases/{case_id}/browser-recorder-instructions", response_model=BrowserRecorderInstructionOut)
def browser_recorder_instructions(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    case = RecorderService(db).get_case(case_id)
    if not case:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return BrowserRecorderInstructionOut(
        recorded_case_id=case_id,
        ingest_url=f"http://127.0.0.1:8000/api/recorder/public/cases/{case_id}/browser-events",
        extension_path="browser_extension/autotest_recorder",
        instructions=[
            "1. Instala la extensión una sola vez desde chrome://extensions.",
            "2. Activa Developer mode y usa Load unpacked.",
            "3. Selecciona la carpeta browser_extension/autotest_recorder.",
            "4. En AutoTest Pro copia el Case ID y la API base.",
            "5. Abre la extensión, pega los datos y presiona Guardar y activar.",
            "6. Abre o recarga el sitio bajo prueba y realiza el flujo normalmente.",
            "7. Regresa a AutoTest Pro y presiona Refrescar pasos o Limpiar duplicados.",
        ],
    )




@router.get("/cases/{case_id}/browser-recorder-status", response_model=BrowserRecorderStatusOut)
def browser_recorder_status(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    status = RecorderService(db).get_browser_recorder_status(case_id)
    if not status:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return status


@router.post("/cases/{case_id}/cleanup", response_model=RecorderCleanupOut)
def cleanup_recorded_steps(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    result = RecorderService(db).cleanup_steps(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return result


@router.delete("/cases/{case_id}/steps", response_model=RecorderCleanupOut)
def clear_recorded_steps(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    result = RecorderService(db).clear_steps(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return result


@router.post("/public/cases/{case_id}/browser-events", response_model=RecordedStepOut)
def ingest_browser_event_public(case_id: int, data: BrowserRecordedEventIn, db: Session = Depends(get_db)):
    """Local browser-extension ingest endpoint.

    This endpoint is intentionally public for the local Chrome extension because
    content scripts cannot reliably send the authenticated HTTPOnly cookie from
    third-party test sites. Keep it bound to localhost in production.
    """
    step = RecorderService(db).add_browser_event(case_id, data)
    if not step:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return step


@router.post("/cases/{case_id}/browser-events", response_model=RecordedStepOut)
def ingest_browser_event_authenticated(
    case_id: int,
    data: BrowserRecordedEventIn,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    step = RecorderService(db).add_browser_event(case_id, data)
    if not step:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return step


@router.post("/cases/{case_id}/run", response_model=ExecutionOut)
def run_recorded_case(
    case_id: int,
    data: RunRecordedCaseRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["executions.run", "recorder.manage"])),
):
    try:
        execution = RecordedExecutionService(db).run_recorded_case(case_id, data)
    except ValueError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    if not execution:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return execution


@router.get("/cases/{case_id}/export/preview", response_model=RecordedCaseExportPreviewOut)
def preview_recorded_case_export(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    generated = CodeExportService(db).preview_export(case_id)
    if not generated:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return RecordedCaseExportPreviewOut(**generated.__dict__)


@router.post("/cases/{case_id}/export", response_model=RecordedCaseExportOut)
def export_recorded_case(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    result = CodeExportService(db).create_export_zip(case_id)
    if not result:
        raise HTTPException(status_code=404, detail="Recorded case not found")
    return result


@router.get("/cases/{case_id}/export/download")
def download_recorded_case_export(
    case_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["recorder.manage"])),
):
    export_service = CodeExportService(db)
    zip_path = export_service.latest_zip_for_case(case_id)
    if not zip_path or not zip_path.exists():
        result = export_service.create_export_zip(case_id)
        if not result:
            raise HTTPException(status_code=404, detail="Recorded case not found")
        zip_path = export_service.latest_zip_for_case(case_id)
    if not zip_path or not zip_path.exists():
        raise HTTPException(status_code=404, detail="Export file not found")
    return FileResponse(
        path=str(zip_path),
        filename=zip_path.name,
        media_type="application/zip",
    )
