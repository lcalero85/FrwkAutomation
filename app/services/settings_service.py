from __future__ import annotations

from sqlalchemy.orm import Session

from app.database.models import Setting
from app.schemas.settings_schema import SettingsPayload

DEFAULT_SETTINGS: dict[str, tuple[str, str, str]] = {
    "app_name": ("AutoTest Pro Framework", "string", "Nombre comercial de la plataforma"),
    "company_name": ("AutoTest Pro", "string", "Empresa o marca propietaria"),
    "support_email": ("support@autotestpro.local", "string", "Correo de soporte"),
    "website_url": ("https://autotestpro.local", "string", "URL pública de la empresa o producto"),
    "logo_text": ("AT", "string", "Texto corto para el logo lateral"),
    "tagline": ("Plataforma de Automatización QA", "string", "Texto superior de la interfaz"),
    "primary_color": ("#2463eb", "string", "Color principal de la interfaz"),
    "secondary_color": ("#0e1930", "string", "Color principal del sidebar"),
    "theme": ("Corporate Light", "string", "Tema visual activo"),
    "language": ("es", "string", "Idioma de la interfaz"),
    "font_family": ("Inter, Segoe UI, Arial, sans-serif", "string", "Fuente base de la interfaz"),
    "font_size": ("15", "number", "Tamaño base de fuente en pixeles (9 a 28)"),
    "timezone": ("America/El_Salvador", "string", "Zona horaria"),
    "reports_path": ("reports", "string", "Ruta de reportes"),
    "logs_path": ("logs", "string", "Ruta de logs"),
    "screenshots_path": ("screenshots", "string", "Ruta de capturas"),
    "videos_path": ("videos", "string", "Ruta de videos"),
    "default_browser": ("chrome", "string", "Navegador por defecto"),
    "default_environment": ("demo", "string", "Ambiente por defecto"),
    "execution_timeout": ("60", "number", "Timeout global de ejecución en segundos"),
    "screenshot_on_failure": ("true", "boolean", "Captura en fallo"),
    "screenshot_each_step": ("false", "boolean", "Captura en cada paso"),
    "date_format": ("YYYY-MM-DD HH:mm", "string", "Formato de fecha visible"),
    "session_timeout_minutes": ("480", "number", "Tiempo de sesión en minutos"),
    "default_parallel_workers": ("2", "number", "Workers paralelos por defecto"),
    "retry_failed_tests": ("false", "boolean", "Reintentar pruebas fallidas"),
    "max_retry_count": ("1", "number", "Cantidad máxima de reintentos"),
    "auto_open_latest_report": ("false", "boolean", "Abrir último reporte al finalizar"),
    "mask_sensitive_data": ("true", "boolean", "Enmascarar datos sensibles en reportes"),
    "audit_retention_days": ("90", "number", "Retención de auditoría en días"),
    "reports_retention_days": ("180", "number", "Retención de reportes en días"),
    "default_report_formats": ("html,excel,pdf", "string", "Formatos de reporte por defecto"),
    "smtp_server": ("", "string", "Servidor SMTP"),
    "smtp_port": ("587", "number", "Puerto SMTP"),
    "smtp_user": ("", "string", "Usuario SMTP"),
    "smtp_password": ("", "password", "Contraseña SMTP o app password"),
    "smtp_sender": ("", "string", "Correo remitente"),
    "smtp_use_tls": ("true", "boolean", "Usar TLS"),
    "smtp_use_ssl": ("false", "boolean", "Usar SSL directo"),
    "smtp_default_recipients": ("", "string", "Destinatarios por defecto"),
}


def ensure_default_settings(db: Session) -> None:
    for key, (value, setting_type, description) in DEFAULT_SETTINGS.items():
        existing = db.query(Setting).filter(Setting.setting_key == key).first()
        if not existing:
            db.add(Setting(
                setting_key=key,
                setting_value=value,
                setting_type=setting_type,
                description=description,
            ))
    db.commit()


def get_settings_dict(db: Session) -> dict[str, str]:
    ensure_default_settings(db)
    rows = db.query(Setting).all()
    values = {row.setting_key: row.setting_value or "" for row in rows}
    for key, (default, _, _) in DEFAULT_SETTINGS.items():
        values.setdefault(key, default)
    return values


def get_settings_payload(db: Session) -> SettingsPayload:
    return SettingsPayload(**get_settings_dict(db))


def update_settings(db: Session, payload: SettingsPayload) -> SettingsPayload:
    ensure_default_settings(db)
    data = payload.model_dump()
    for key, value in data.items():
        setting = db.query(Setting).filter(Setting.setting_key == key).first()
        default_type = DEFAULT_SETTINGS.get(key, ("", "string", ""))[1]
        default_desc = DEFAULT_SETTINGS.get(key, ("", "string", ""))[2]
        if setting:
            if key == "smtp_password" and (value is None or str(value).strip() == ""):
                continue
            setting.setting_value = str(value) if value is not None else ""
            setting.setting_type = setting.setting_type or default_type
        else:
            db.add(Setting(
                setting_key=key,
                setting_value=str(value) if value is not None else "",
                setting_type=default_type,
                description=default_desc,
            ))
    db.commit()
    return get_settings_payload(db)


def reset_settings(db: Session) -> SettingsPayload:
    for key, (value, setting_type, description) in DEFAULT_SETTINGS.items():
        setting = db.query(Setting).filter(Setting.setting_key == key).first()
        if not setting:
            db.add(Setting(setting_key=key, setting_value=value, setting_type=setting_type, description=description))
        else:
            setting.setting_value = value
            setting.setting_type = setting_type
            setting.description = description
    db.commit()
    return get_settings_payload(db)
