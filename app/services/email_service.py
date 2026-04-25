from __future__ import annotations

import mimetypes
import os
import smtplib
from dataclasses import dataclass
from email.message import EmailMessage
from pathlib import Path
from typing import Iterable

from sqlalchemy.orm import Session

from app.database.connection import PROJECT_ROOT
from app.database.models import Report
from app.services.settings_service import get_settings_dict


@dataclass
class SmtpConfig:
    server: str
    port: int
    username: str
    password: str
    sender: str
    use_tls: bool
    use_ssl: bool
    default_recipients: str


def _as_bool(value: str | bool | None, default: bool = False) -> bool:
    if isinstance(value, bool):
        return value
    if value is None:
        return default
    return str(value).strip().lower() in {"1", "true", "yes", "si", "sí", "y"}


def get_smtp_config(db: Session) -> SmtpConfig:
    settings = get_settings_dict(db)
    port_raw = settings.get("smtp_port") or "587"
    try:
        port = int(port_raw)
    except ValueError:
        port = 587

    return SmtpConfig(
        server=(settings.get("smtp_server") or "").strip(),
        port=port,
        username=(settings.get("smtp_user") or "").strip(),
        password=settings.get("smtp_password") or os.getenv("SMTP_PASSWORD", ""),
        sender=(settings.get("smtp_sender") or settings.get("smtp_user") or "").strip(),
        use_tls=_as_bool(settings.get("smtp_use_tls"), True),
        use_ssl=_as_bool(settings.get("smtp_use_ssl"), False),
        default_recipients=settings.get("smtp_default_recipients") or "",
    )


def parse_recipients(value: str | Iterable[str] | None) -> list[str]:
    if value is None:
        return []
    if not isinstance(value, str):
        return [str(item).strip() for item in value if str(item).strip()]
    normalized = value.replace(";", ",").replace("\n", ",")
    return [item.strip() for item in normalized.split(",") if item.strip()]


def validate_smtp_config(config: SmtpConfig) -> None:
    missing = []
    if not config.server:
        missing.append("Servidor SMTP")
    if not config.sender:
        missing.append("Correo remitente")
    if not config.username:
        missing.append("Usuario SMTP")
    if not config.password:
        missing.append("Contraseña SMTP")
    if missing:
        raise ValueError("Configuración SMTP incompleta: " + ", ".join(missing))


def _resolve_path(path_value: str | None) -> Path | None:
    if not path_value:
        return None
    path = Path(path_value)
    if not path.is_absolute():
        path = PROJECT_ROOT / path
    return path if path.exists() and path.is_file() else None


def get_report_attachments(report: Report, include_html: bool = True, include_excel: bool = True, include_pdf: bool = True) -> list[Path]:
    candidates: list[str | None] = []
    if include_html:
        candidates.append(report.html_path)
    if include_excel:
        candidates.append(report.excel_path)
    if include_pdf:
        candidates.append(report.pdf_path)

    paths: list[Path] = []
    seen: set[str] = set()
    for candidate in candidates:
        resolved = _resolve_path(candidate)
        if not resolved:
            continue
        key = str(resolved.resolve())
        if key not in seen:
            paths.append(resolved)
            seen.add(key)
    return paths


def build_message(sender: str, recipients: list[str], subject: str, body: str, attachments: list[Path] | None = None) -> EmailMessage:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = ", ".join(recipients)
    msg["Subject"] = subject
    msg.set_content(body)

    for file_path in attachments or []:
        content_type, _ = mimetypes.guess_type(str(file_path))
        maintype, subtype = (content_type or "application/octet-stream").split("/", 1)
        with file_path.open("rb") as fh:
            msg.add_attachment(fh.read(), maintype=maintype, subtype=subtype, filename=file_path.name)
    return msg


def send_email(db: Session, recipients: list[str], subject: str, body: str, attachments: list[Path] | None = None) -> dict:
    config = get_smtp_config(db)
    validate_smtp_config(config)
    if not recipients:
        recipients = parse_recipients(config.default_recipients)
    if not recipients:
        raise ValueError("No se definieron destinatarios para el correo")

    message = build_message(config.sender, recipients, subject, body, attachments)

    if config.use_ssl:
        with smtplib.SMTP_SSL(config.server, config.port, timeout=30) as smtp:
            smtp.login(config.username, config.password)
            smtp.send_message(message)
    else:
        with smtplib.SMTP(config.server, config.port, timeout=30) as smtp:
            smtp.ehlo()
            if config.use_tls:
                smtp.starttls()
                smtp.ehlo()
            smtp.login(config.username, config.password)
            smtp.send_message(message)

    return {
        "success": True,
        "recipients": recipients,
        "attachments": [str(path) for path in attachments or []],
    }


def send_test_email(db: Session, recipient: str) -> dict:
    return send_email(
        db=db,
        recipients=[recipient],
        subject="Prueba SMTP - AutoTest Pro Framework",
        body=(
            "Este es un correo de prueba enviado desde AutoTest Pro Framework.\n\n"
            "Si recibiste este mensaje, la configuración SMTP está funcionando correctamente."
        ),
        attachments=[],
    )


def send_report_email(
    db: Session,
    report: Report,
    recipients: list[str],
    subject: str | None = None,
    message: str | None = None,
    include_html: bool = True,
    include_excel: bool = True,
    include_pdf: bool = True,
) -> dict:
    attachments = get_report_attachments(report, include_html, include_excel, include_pdf)
    if not attachments:
        raise ValueError("No se encontraron archivos físicos para adjuntar al correo")

    execution = report.execution
    default_subject = f"Reporte de ejecución #{execution.id if execution else report.execution_id} - AutoTest Pro"
    default_body = (
        "Hola,\n\n"
        "Se adjunta el reporte generado por AutoTest Pro Framework.\n\n"
        f"ID de ejecución: {report.execution_id}\n"
        f"Estado: {execution.status if execution else 'N/A'}\n"
        f"Navegador: {execution.browser if execution else 'N/A'}\n"
        f"Ambiente: {execution.environment if execution else 'N/A'}\n\n"
        "Saludos."
    )
    return send_email(
        db=db,
        recipients=recipients,
        subject=subject or default_subject,
        body=message or default_body,
        attachments=attachments,
    )
