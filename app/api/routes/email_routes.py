from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.database.connection import get_db
from app.database.models import Report, User
from app.schemas.email_schema import EmailRecipientPayload, EmailSendResponse, TestEmailPayload
from app.security.auth_utils import require_permissions
from app.services.audit_service import write_audit_log
from app.services.email_service import parse_recipients, send_report_email, send_test_email

router = APIRouter(prefix="/email", tags=["Email"])


@router.post("/test", response_model=EmailSendResponse)
def test_smtp_email(
    payload: TestEmailPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["settings.manage"])),
):
    try:
        result = send_test_email(db, str(payload.recipient))
        write_audit_log(db, action="SMTP_TEST_SENT", module="Email", user=current_user, description=f"SMTP test email sent to {payload.recipient}", request=request)
        return EmailSendResponse(success=True, message="Correo de prueba enviado correctamente", recipients=result["recipients"], attachments=[])
    except Exception as exc:
        write_audit_log(db, action="SMTP_TEST_FAILED", module="Email", user=current_user, description=str(exc), request=request, status="FAILED")
        raise HTTPException(status_code=400, detail=str(exc)) from exc


@router.post("/reports/{report_id}/send", response_model=EmailSendResponse)
def send_report_by_email(
    report_id: int,
    payload: EmailRecipientPayload,
    request: Request,
    db: Session = Depends(get_db),
    current_user: User = Depends(require_permissions(["reports.email"])),
):
    report = db.query(Report).filter(Report.id == report_id).first()
    if not report:
        raise HTTPException(status_code=404, detail="Reporte no encontrado")

    try:
        recipients = parse_recipients(payload.recipients)
        result = send_report_email(
            db=db,
            report=report,
            recipients=recipients,
            subject=payload.subject,
            message=payload.message,
            include_html=payload.include_html,
            include_excel=payload.include_excel,
            include_pdf=payload.include_pdf,
        )
        write_audit_log(db, action="REPORT_EMAIL_SENT", module="Reports", user=current_user, description=f"Report {report_id} sent to {', '.join(result['recipients'])}", request=request)
        return EmailSendResponse(success=True, message="Reporte enviado correctamente", recipients=result["recipients"], attachments=result["attachments"])
    except Exception as exc:
        write_audit_log(db, action="REPORT_EMAIL_FAILED", module="Reports", user=current_user, description=f"Report {report_id}: {exc}", request=request, status="FAILED")
        raise HTTPException(status_code=400, detail=str(exc)) from exc
