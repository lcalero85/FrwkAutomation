from __future__ import annotations

from pathlib import Path

from fastapi import APIRouter, Form, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy.orm import Session

from app.database.connection import SessionLocal
from app.security.auth_utils import COOKIE_NAME, create_access_token, decode_token, get_token_from_request, get_user_permissions
from app.services.auth_service import authenticate_user
from app.services.audit_service import write_audit_log
from app.services.settings_service import get_settings_payload

PROJECT_ROOT = Path(__file__).resolve().parents[3]
TEMPLATES_DIR = PROJECT_ROOT / "app" / "web" / "templates"
templates = Jinja2Templates(directory=str(TEMPLATES_DIR))

router = APIRouter(tags=["Web Interface"])


def get_branding(db: Session) -> dict:
    settings = get_settings_payload(db)
    return settings.model_dump()


def get_ui_user(request: Request):
    token = get_token_from_request(request)
    if not token:
        return None
    username = decode_token(token)
    if not username:
        return None

    db: Session = SessionLocal()
    try:
        from app.database.models import User
        user = db.query(User).filter(User.username == username, User.is_active == True).first()
        if not user:
            return None
        return {
            "id": user.id,
            "username": user.username,
            "full_name": user.full_name,
            "email": user.email,
            "role": user.role.name if user.role else None,
            "permissions": get_user_permissions(db, user),
        }
    finally:
        db.close()


def render(request: Request, template_name: str, active: str, title: str):
    current_user = get_ui_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)

    db: Session = SessionLocal()
    try:
        branding = get_branding(db)
    finally:
        db.close()

    context = {
        "request": request,
        "active": active,
        "title": title,
        "app_name": branding.get("app_name", "AutoTest Pro Framework"),
        "version": "0.18.0",
        "current_user": current_user,
        "branding": branding,
    }
    return templates.TemplateResponse(request, template_name, context)


@router.get("/login", response_class=HTMLResponse)
def login_page(request: Request):
    if get_ui_user(request):
        return RedirectResponse(url="/ui", status_code=302)
    db: Session = SessionLocal()
    try:
        branding = get_branding(db)
    finally:
        db.close()
    return templates.TemplateResponse(request, "login.html", {"request": request, "error": None, "app_name": branding.get("app_name"), "branding": branding})


@router.post("/login", response_class=HTMLResponse)
def login_submit(request: Request, username: str = Form(...), password: str = Form(...)):
    db: Session = SessionLocal()
    try:
        branding = get_branding(db)
        user = authenticate_user(db, username, password)
        if not user:
            write_audit_log(db, action="LOGIN_FAILED", module="Authentication", username=username, description="Invalid web login attempt.", request=request, status="FAILED")
            return templates.TemplateResponse(
                request,
                "login.html",
                {"request": request, "error": "Usuario o contraseña inválidos", "app_name": branding.get("app_name"), "branding": branding},
                status_code=401,
            )

        write_audit_log(db, action="LOGIN_SUCCESS", module="Authentication", user=user, description="User logged in from web form.", request=request, status="SUCCESS")
        token = create_access_token(user.username)
        response = RedirectResponse(url="/ui", status_code=302)
        response.set_cookie(
            key=COOKIE_NAME,
            value=token,
            httponly=True,
            samesite="lax",
            secure=False,
            max_age=60 * 60 * 8,
        )
        return response
    finally:
        db.close()


@router.get("/logout")
def logout_page():
    response = RedirectResponse(url="/login", status_code=302)
    response.delete_cookie(COOKIE_NAME)
    return response


@router.get("/ui", response_class=HTMLResponse)
def ui_dashboard(request: Request):
    return render(request, "dashboard.html", "dashboard", "Dashboard")


@router.get("/ui/projects", response_class=HTMLResponse)
def ui_projects(request: Request):
    return render(request, "projects.html", "projects", "Proyectos")


@router.get("/ui/executions", response_class=HTMLResponse)
def ui_executions(request: Request):
    return render(request, "executions.html", "executions", "Ejecuciones")


@router.get("/ui/reports", response_class=HTMLResponse)
def ui_reports(request: Request):
    return render(request, "reports.html", "reports", "Reportes")


@router.get("/ui/executions/{execution_id}", response_class=HTMLResponse)
def ui_execution_detail(request: Request, execution_id: int):
    return render(request, "execution_detail.html", "executions", f"Detalle de ejecución #{execution_id}")


@router.get("/ui/recorder", response_class=HTMLResponse)
def ui_recorder(request: Request):
    return render(request, "recorder.html", "recorder", "Grabador de pasos")


@router.get("/ui/scheduler", response_class=HTMLResponse)
def ui_scheduler(request: Request):
    return render(request, "scheduler.html", "scheduler", "Scheduler y orquestador")


@router.get("/ui/users", response_class=HTMLResponse)
def ui_users(request: Request):
    return render(request, "users.html", "users", "Usuarios y roles")


@router.get("/ui/profile", response_class=HTMLResponse)
def ui_profile(request: Request):
    return render(request, "profile.html", "profile", "Perfil y seguridad")


@router.get("/ui/audit", response_class=HTMLResponse)
def ui_audit(request: Request):
    current_user = get_ui_user(request)
    if not current_user:
        return RedirectResponse(url="/login", status_code=302)
    if "security.audit" not in current_user.get("permissions", []):
        return RedirectResponse(url="/ui", status_code=302)
    return render(request, "audit.html", "audit", "Auditoría")


@router.get("/ui/templates", response_class=HTMLResponse)
def ui_templates(request: Request):
    return render(request, "templates.html", "templates", "Plantillas profesionales")


@router.get("/ui/settings", response_class=HTMLResponse)
def ui_settings(request: Request):
    return render(request, "settings.html", "settings", "Configuraciones")
